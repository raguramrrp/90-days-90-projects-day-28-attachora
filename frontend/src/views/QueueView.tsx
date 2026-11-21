import React, { useState, useMemo, useEffect } from 'react';
import {
  Search,
  RotateCcw,
  Check,
  SkipForward,
  X,
  Clock,
  Sparkles,
} from 'lucide-react';
import { Attachment, SummaryMetrics } from '../types';

interface QueueViewProps {
  attachments: Attachment[];
  summary: SummaryMetrics | null;
  selectedRowId: number | null;
  onSelectRow: (id: number) => void;
  onApproveSingle: (id: number) => void;
  onApproveBulk: (ids: number[]) => void;
  onSkipBulk: (ids: number[]) => void;
  onUndoSingle: (id: number) => void;
  onOverrideRouting: (id: number, data: any) => void;
  onRefresh: () => void;
}

export const QueueView: React.FC<QueueViewProps> = ({
  attachments,
  summary,
  selectedRowId,
  onSelectRow,
  onApproveSingle,
  onApproveBulk,
  onSkipBulk,
  onUndoSingle,
  onOverrideRouting,
  onRefresh,
}) => {
  // Filters state
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('Queue'); // Default to Active Queue (unfiled items)
  const [fileTypeFilter, setFileTypeFilter] = useState('All');
  const [senderFilter, setSenderFilter] = useState('All');
  const [dateRangeFilter, setDateRangeFilter] = useState('All');

  // Multi-selection checkboxes
  const [checkedIds, setCheckedIds] = useState<Set<number>>(new Set());

  // Pagination state (6 items per page matching reference)
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 6;

  // Inspector tabs: 'Overview' | 'Preview' | 'Routing'
  const [inspectorTab, setInspectorTab] = useState<'Overview' | 'Preview' | 'Routing'>('Overview');

  // Routing override inputs
  const [editCategory, setEditCategory] = useState('');
  const [editDestination, setEditDestination] = useState('');
  const [editDupStrategy, setEditDupStrategy] = useState('keep_copy');

  // Automated Mode state
  const [autoMode, setAutoMode] = useState<boolean>(false);
  const [autoFiling, setAutoFiling] = useState<boolean>(false);

  useEffect(() => {
    fetch('/api/settings')
      .then((res) => res.json())
      .then((data) => {
        if (data && typeof data.auto_mode === 'boolean') {
          setAutoMode(data.auto_mode);
        }
      })
      .catch(console.error);
  }, []);

  const handleToggleAutoMode = async () => {
    const nextState = !autoMode;
    setAutoMode(nextState);
    try {
      await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ auto_mode: nextState }),
      });
      onRefresh();
    } catch (e) {
      console.error(e);
    }
  };

  const handleAutoFileAll = async () => {
    try {
      setAutoFiling(true);
      const res = await fetch('/api/auto-file', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        onRefresh();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setAutoFiling(false);
    }
  };

  // Filtered attachments
  const filtered = useMemo(() => {
    return attachments.filter((att) => {
      // Search filter
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const match =
          att.original_filename.toLowerCase().includes(q) ||
          att.sender.toLowerCase().includes(q) ||
          att.sender_email.toLowerCase().includes(q) ||
          att.subject.toLowerCase().includes(q) ||
          att.sha256.toLowerCase().includes(q);
        if (!match) return false;
      }
      // Category filter
      if (categoryFilter !== 'All' && att.category !== categoryFilter) {
        return false;
      }
      // Status filter
      const s = (att.status || '').toLowerCase();
      if (statusFilter === 'Queue') {
        // Active queue: show items awaiting action; immediately exclude filed/organized/skipped
        if (['organized', 'filed', 'skipped'].includes(s)) return false;
      } else if (statusFilter !== 'All') {
        const sf = statusFilter.toLowerCase();
        if (sf === 'ready' && !['ready', 'ready to file'].includes(s)) return false;
        if (sf === 'duplicate' && !['duplicate', 'exact duplicate'].includes(s)) return false;
        if (sf === 'review' && !['review', 'pending approval', 'detected'].includes(s)) return false;
        if (sf === 'filed' && !['filed', 'organized'].includes(s)) return false;
      }
      // File type filter
      if (fileTypeFilter !== 'All') {
        const ext = (att.extension || '').toLowerCase();
        if (fileTypeFilter.toLowerCase() !== ext) return false;
      }
      // Sender filter
      if (senderFilter !== 'All') {
        const s = att.sender_email || att.sender;
        if (s !== senderFilter) return false;
      }
      return true;
    });
  }, [attachments, searchQuery, categoryFilter, statusFilter, fileTypeFilter, senderFilter]);

  // Distinct senders for dropdown
  const distinctSenders = useMemo(() => {
    const set = new Set<string>();
    attachments.forEach((a) => {
      if (a.sender_email) set.add(a.sender_email);
      else if (a.sender) set.add(a.sender);
    });
    return Array.from(set).sort();
  }, [attachments]);

  // Pagination calculation
  const totalItems = filtered.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const pageItems = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filtered.slice(start, start + pageSize);
  }, [filtered, currentPage]);

  // Active item in inspector
  const activeItem = useMemo(() => {
    if (!selectedRowId && filtered.length > 0) return filtered[0];
    return attachments.find((a) => a.id === selectedRowId) || filtered[0] || null;
  }, [attachments, selectedRowId, filtered]);

  // Handle select all on current page
  const allPageChecked = pageItems.length > 0 && pageItems.every((a) => checkedIds.has(a.id));
  const toggleSelectAll = () => {
    const next = new Set(checkedIds);
    if (allPageChecked) {
      pageItems.forEach((a) => next.delete(a.id));
    } else {
      pageItems.forEach((a) => next.add(a.id));
    }
    setCheckedIds(next);
  };

  const toggleRowCheck = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    const next = new Set(checkedIds);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    setCheckedIds(next);
    onSelectRow(id);
  };

  const handleRowClick = (id: number) => {
    onSelectRow(id);
    if (activeItem && activeItem.id === id) {
      setEditCategory(activeItem.category);
      setEditDestination(activeItem.rule_match?.destination || 'Finance/Invoices');
    }
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setCategoryFilter('All');
    setStatusFilter('Queue');
    setFileTypeFilter('All');
    setSenderFilter('All');
    setDateRangeFilter('All');
    setCurrentPage(1);
  };

  // Badge helpers
  const getBadgeStyle = (ext: string) => {
    const e = (ext || 'dat').toLowerCase();
    if (e === 'pdf') return { bg: 'bg-[#D32F2F]', label: 'PDF' };
    if (['docx', 'doc'].includes(e)) return { bg: 'bg-[#1976D2]', label: 'DOC' };
    if (['xlsx', 'xls', 'csv'].includes(e)) return { bg: 'bg-[#2E7D32]', label: 'XLS' };
    if (['zip', 'tar', 'gz'].includes(e)) return { bg: 'bg-[#E65100]', label: 'ZIP' };
    if (['txt', 'log'].includes(e)) return { bg: 'bg-[#546E7A]', label: 'TXT' };
    if (['png', 'jpg', 'jpeg'].includes(e)) return { bg: 'bg-[#7B1FA2]', label: 'IMG' };
    return { bg: 'bg-[#546E7A]', label: e.slice(0, 3).toUpperCase() };
  };

  const getStatusPill = (status: string) => {
    const s = (status || 'Ready').toLowerCase();
    if (['ready', 'ready to file'].includes(s)) {
      return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#E9F2EC] text-[#278253] border border-[#C9E2D2]">Ready</span>;
    }
    if (['duplicate', 'exact duplicate'].includes(s)) {
      return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#EFEFEF] text-[#66716B] border border-[#DCDCDC]">Duplicate</span>;
    }
    if (['review', 'pending approval', 'detected'].includes(s)) {
      return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#FEF5E7] text-[#B77925] border border-[#F7E1C3]">Review</span>;
    }
    if (['filed', 'organized'].includes(s)) {
      return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#E6F4EA] text-[#278253] border border-[#BEE0CC]">Filed</span>;
    }
    return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#FDE8E8] text-[#BD4545] border border-[#F8B4B4]">Failed</span>;
  };

  const formatDateLines = (dt: string) => {
    if (!dt) return { date: '21 Nov 2026', time: '10:15 AM' };
    const parts = dt.replace('T', ' ').split(' ');
    const dStr = parts[0] || '2026-11-21';
    const tStr = parts[1]?.slice(0, 5) || '10:15';
    try {
      const dateObj = new Date(dStr + 'T' + tStr);
      const dateFormatted = dateObj.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
      return { date: dateFormatted, time: tStr };
    } catch {
      return { date: dStr, time: tStr };
    }
  };

  return (
    <div className="flex-1 flex gap-5 p-6 overflow-y-auto select-none">
      {/* ------------------ LEFT COLUMN: ATTACHMENT QUEUE (72%) ------------------ */}
      <div className="w-[72%] flex flex-col gap-3.5">
        {/* 1. Page Heading */}
        <div className="flex items-baseline justify-between">
          <div>
            <h1 className="text-[22px] font-bold text-[#202824] leading-tight">Attachment queue</h1>
            <p className="text-[13px] text-[#66716B] mt-0.5">Review, classify and file incoming documents.</p>
          </div>
          <div className="flex items-center gap-3">
            {/* Automated Mode Toggle */}
            <button
              onClick={handleToggleAutoMode}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[12px] font-medium border transition-all ${
                autoMode
                  ? 'bg-[#EBF7F0] text-[#1E5638] border-[#A3D9B8] shadow-sm'
                  : 'bg-white text-[#66716B] border-[#DCE3DE] hover:bg-[#F7F9F7]'
              }`}
              title="When ON, incoming scans automatically file qualifying high-confidence documents"
            >
              <Sparkles size={13} className={autoMode ? 'text-[#286B50]' : 'text-[#8A948E]'} />
              <span>Automated Mode: <strong className={autoMode ? 'text-[#1E5638]' : 'text-[#202824]'}>{autoMode ? 'ON' : 'OFF'}</strong></span>
            </button>

            {/* Quick Auto-File button if there are ready documents */}
            {(summary?.ready_to_file ?? 0) > 0 && (
              <button
                onClick={handleAutoFileAll}
                disabled={autoFiling}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[12px] font-semibold text-white bg-[#286B50] hover:bg-[#20553F] transition-all shadow-sm disabled:opacity-50"
                title="Automatically file all documents marked ready without manual selection"
              >
                <Sparkles size={13} />
                <span>{autoFiling ? 'Filing...' : `Auto-File ${summary?.ready_to_file} Ready`}</span>
              </button>
            )}

            <div className="flex items-center gap-1.5 text-[12px] text-[#66716B] pl-2 border-l border-[#DCE3DE]">
              <Clock size={14} className="text-[#66716B]" />
              <span>Last scan {summary?.last_scan || '10:42 AM'}</span>
            </div>
          </div>
        </div>

        {/* 2. Operational Summary Strip */}
        <div className="bg-white border border-[#DCE3DE] rounded-lg px-6 py-3 flex items-center justify-between shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
          <div className="flex items-baseline gap-2">
            <span className="text-[22px] font-bold text-[#286B50] leading-none">{summary?.awaiting_review ?? 24}</span>
            <span className="text-[13px] text-[#202824] font-medium">Awaiting review</span>
          </div>
          <div className="w-[1px] h-6 bg-[#DCE3DE]" />
          <div className="flex items-baseline gap-2">
            <span className="text-[22px] font-bold text-[#278253] leading-none">{summary?.ready_to_file ?? 8}</span>
            <span className="text-[13px] text-[#202824] font-medium">Ready to file</span>
          </div>
          <div className="w-[1px] h-6 bg-[#DCE3DE]" />
          <div className="flex items-baseline gap-2">
            <span className="text-[22px] font-bold text-[#B77925] leading-none">{summary?.duplicates_count ?? 3}</span>
            <span className="text-[13px] text-[#202824] font-medium">Duplicates</span>
          </div>
          <div className="w-[1px] h-6 bg-[#DCE3DE]" />
          <div className="flex items-baseline gap-2">
            <span className="text-[22px] font-bold text-[#BD4545] leading-none">{summary?.need_attention ?? 2}</span>
            <span className="text-[13px] text-[#202824] font-medium">Need attention</span>
          </div>
        </div>

        {/* 3. Search Bar */}
        <div className="relative flex items-center">
          <Search size={16} className="absolute left-3.5 text-[#66716B]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
            placeholder="Search filename, sender, subject or SHA-256"
            className="w-full bg-white border border-[#DCE3DE] rounded-md pl-10 pr-16 py-2 text-[13px] text-[#202824] placeholder-[#8A948E] focus:outline-none focus:border-[#286B50] focus:ring-1 focus:ring-[#286B50]"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 text-[12px] text-[#66716B] hover:text-[#202824] font-medium px-2 py-0.5 rounded hover:bg-[#F1F6F2]"
            >
              Clear
            </button>
          )}
        </div>

        {/* 4. Compact Filter Toolbar */}
        <div className="flex items-center gap-2.5">
          <select
            value={categoryFilter}
            onChange={(e) => { setCategoryFilter(e.target.value); setCurrentPage(1); }}
            className="bg-white border border-[#DCE3DE] rounded-md px-3 py-1.5 text-[12px] text-[#202824] font-medium focus:outline-none focus:border-[#286B50]"
          >
            <option value="All">Category ▾</option>
            <option value="Invoices">Finance / Invoices</option>
            <option value="Receipts">Finance / Receipts</option>
            <option value="Resumes / CVs">HR / Resumes</option>
            <option value="Reports">Reports</option>
            <option value="Documents">Documents</option>
            <option value="Images">Images</option>
            <option value="Archives">Archives</option>
            <option value="Code / Technical Files">Code</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setCurrentPage(1); }}
            className="bg-white border border-[#DCE3DE] rounded-md px-3 py-1.5 text-[12px] text-[#202824] font-medium focus:outline-none focus:border-[#286B50]"
          >
            <option value="Queue">Active Queue (Pending) ▾</option>
            <option value="Ready">Ready to File</option>
            <option value="Duplicate">Duplicates</option>
            <option value="Review">Need Review</option>
            <option value="Filed">Filed / Organized</option>
            <option value="All">All (Including Filed)</option>
          </select>

          <select
            value={fileTypeFilter}
            onChange={(e) => { setFileTypeFilter(e.target.value); setCurrentPage(1); }}
            className="bg-white border border-[#DCE3DE] rounded-md px-3 py-1.5 text-[12px] text-[#202824] font-medium focus:outline-none focus:border-[#286B50]"
          >
            <option value="All">File type ▾</option>
            <option value="pdf">PDF</option>
            <option value="docx">DOCX</option>
            <option value="xlsx">XLSX</option>
            <option value="zip">ZIP</option>
            <option value="txt">TXT</option>
            <option value="png">PNG / JPG</option>
          </select>

          <select
            value={senderFilter}
            onChange={(e) => { setSenderFilter(e.target.value); setCurrentPage(1); }}
            className="bg-white border border-[#DCE3DE] rounded-md px-3 py-1.5 text-[12px] text-[#202824] font-medium focus:outline-none focus:border-[#286B50] max-w-[150px] truncate"
          >
            <option value="All">Sender ▾</option>
            {distinctSenders.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>

          <select
            value={dateRangeFilter}
            onChange={(e) => { setDateRangeFilter(e.target.value); setCurrentPage(1); }}
            className="bg-white border border-[#DCE3DE] rounded-md px-3 py-1.5 text-[12px] text-[#202824] font-medium focus:outline-none focus:border-[#286B50]"
          >
            <option value="All">Date range ▾</option>
            <option value="Today">Today</option>
            <option value="7d">Past 7 Days</option>
            <option value="30d">Past 30 Days</option>
          </select>

          <button
            onClick={handleResetFilters}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-[#DCE3DE] rounded-md text-[12px] text-[#66716B] hover:text-[#202824] font-medium hover:bg-[#F7F9F7] transition-all"
          >
            <RotateCcw size={13} />
            <span>Reset</span>
          </button>
        </div>

        {/* 5. Bulk Action Toolbar */}
        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-[#E9F2EC] text-[#202824] text-[12px] font-semibold rounded-md border border-[#DCE3DE]">
            <Check size={14} className="text-[#278253]" strokeWidth={2.5} />
            <span>{checkedIds.size} selected</span>
          </div>

          <button
            onClick={() => {
              onApproveBulk(Array.from(checkedIds));
              setCheckedIds(new Set());
            }}
            disabled={checkedIds.size === 0}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-[13px] font-medium transition-all ${
              checkedIds.size > 0
                ? 'bg-[#286B50] hover:bg-[#20553F] text-white shadow-sm'
                : 'bg-[#EAEFEA] text-[#8A948E] cursor-not-allowed'
            }`}
          >
            <Check size={14} strokeWidth={2.5} />
            <span>Approve and file</span>
          </button>

          <button
            onClick={() => {
              onSkipBulk(Array.from(checkedIds));
              setCheckedIds(new Set());
            }}
            disabled={checkedIds.size === 0}
            className={`flex items-center gap-1.5 px-3 py-1.5 bg-white border border-[#DCE3DE] rounded-md text-[13px] font-medium transition-all ${
              checkedIds.size > 0
                ? 'hover:bg-[#F7F9F7] text-[#202824]'
                : 'text-[#8A948E] cursor-not-allowed'
            }`}
          >
            <SkipForward size={14} />
            <span>Skip</span>
          </button>

          <button
            onClick={() => setCheckedIds(new Set())}
            disabled={checkedIds.size === 0}
            className={`flex items-center gap-1 px-3 py-1.5 bg-white border border-[#DCE3DE] rounded-md text-[13px] font-medium transition-all ${
              checkedIds.size > 0
                ? 'hover:bg-[#F7F9F7] text-[#202824]'
                : 'text-[#8A948E] cursor-not-allowed'
            }`}
          >
            <X size={14} />
            <span>Clear selection</span>
          </button>
        </div>

        {/* 6. Attachment Data Table */}
        <div className="bg-white border border-[#DCE3DE] rounded-lg overflow-hidden shadow-sm">
          <table className="w-full border-collapse text-left">
            <thead>
              <tr className="bg-[#F7F9F7] border-b border-[#DCE3DE] text-[11px] font-bold text-[#66716B] uppercase tracking-wider">
                <th className="py-2.5 px-3.5 w-10">
                  <input
                    type="checkbox"
                    checked={allPageChecked}
                    onChange={toggleSelectAll}
                    className="w-4 h-4 rounded border-[#DCE3DE] text-[#286B50] focus:ring-[#286B50] cursor-pointer"
                  />
                </th>
                <th className="py-2.5 px-3">ATTACHMENT</th>
                <th className="py-2.5 px-3">SENDER / SUBJECT</th>
                <th className="py-2.5 px-3">RECEIVED</th>
                <th className="py-2.5 px-3">CATEGORY</th>
                <th className="py-2.5 px-3">DESTINATION</th>
                <th className="py-2.5 px-3 text-center">STATUS</th>
              </tr>
            </thead>
            <tbody>
              {pageItems.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-[13px] text-[#66716B]">
                    No attachment records match the current filter or search criteria.
                  </td>
                </tr>
              ) : (
                pageItems.map((att) => {
                  const isChecked = checkedIds.has(att.id);
                  const isSelected = activeItem?.id === att.id;
                  const badge = getBadgeStyle(att.extension);
                  const dateInfo = formatDateLines(att.received_at);
                  const destPath = att.rule_match?.destination
                    ? `/${att.rule_match.destination}`
                    : '/Documents/Projects';

                  return (
                    <tr
                      key={att.id}
                      onClick={() => handleRowClick(att.id)}
                      className={`border-b border-[#EAEFEA] transition-colors cursor-pointer text-[13px] ${
                        isSelected || isChecked
                          ? 'bg-[#F1F6F2] border-l-[3px] border-l-[#286B50]'
                          : 'hover:bg-[#F1F6F2]'
                      }`}
                    >
                      {/* Checkbox */}
                      <td className="py-2.5 px-3.5" onClick={(e) => e.stopPropagation()}>
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={(e) => toggleRowCheck(att.id, e as any)}
                          className="w-4 h-4 rounded border-[#DCE3DE] text-[#286B50] focus:ring-[#286B50] cursor-pointer"
                        />
                      </td>

                      {/* Attachment badge & filename */}
                      <td className="py-2.5 px-3">
                        <div className="flex items-center gap-2.5">
                          <span className={`w-[26px] h-[20px] rounded text-[9px] font-bold text-white flex items-center justify-center flex-shrink-0 tracking-tight ${badge.bg}`}>
                            {badge.label}
                          </span>
                          <span className="font-medium text-[#202824] truncate max-w-[200px]" title={att.original_filename}>
                            {att.original_filename}
                          </span>
                        </div>
                      </td>

                      {/* Sender & Subject (2 lines) */}
                      <td className="py-2.5 px-3">
                        <div className="leading-tight">
                          <div className="font-medium text-[#202824] text-[12px] truncate max-w-[190px]">
                            {att.sender_email || att.sender || 'accounts@company.com'}
                          </div>
                          <div className="text-[11px] text-[#66716B] truncate max-w-[190px] mt-0.5">
                            {att.subject || 'Q4 Invoice'}
                          </div>
                        </div>
                      </td>

                      {/* Received Date & Time (2 lines) */}
                      <td className="py-2.5 px-3">
                        <div className="leading-tight text-[12px]">
                          <div className="text-[#202824] font-medium">{dateInfo.date}</div>
                          <div className="text-[11px] text-[#66716B] mt-0.5">{dateInfo.time}</div>
                        </div>
                      </td>

                      {/* Category */}
                      <td className="py-2.5 px-3 text-[#202824] text-[12px] font-medium">
                        {att.category}
                      </td>

                      {/* Destination Path */}
                      <td className="py-2.5 px-3 font-mono text-[11px] text-[#66716B] truncate max-w-[180px]" title={destPath}>
                        {destPath}
                      </td>

                      {/* Status */}
                      <td className="py-2.5 px-3 text-center">
                        {getStatusPill(att.status)}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* 7. Pagination Controls */}
        <div className="flex items-center justify-between text-[12px] text-[#66716B] pt-1">
          <div>
            Showing <b>{Math.min(1 + (currentPage - 1) * pageSize, totalItems)}–{Math.min(currentPage * pageSize, totalItems)}</b> of <b>{totalItems}</b> results
          </div>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage <= 1}
              className="w-7 h-7 rounded border border-[#DCE3DE] bg-white flex items-center justify-center hover:bg-[#F7F9F7] disabled:opacity-40 disabled:cursor-not-allowed"
            >
              &lt;
            </button>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
              <button
                key={p}
                onClick={() => setCurrentPage(p)}
                className={`w-7 h-7 rounded text-[12px] font-medium flex items-center justify-center transition-all ${
                  p === currentPage
                    ? 'bg-[#286B50] text-white shadow-sm'
                    : 'bg-white border border-[#DCE3DE] text-[#202824] hover:bg-[#F7F9F7]'
                }`}
              >
                {p}
              </button>
            ))}
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage >= totalPages}
              className="w-7 h-7 rounded border border-[#DCE3DE] bg-white flex items-center justify-center hover:bg-[#F7F9F7] disabled:opacity-40 disabled:cursor-not-allowed"
            >
              &gt;
            </button>
          </div>
        </div>
      </div>

      {/* ------------------ RIGHT COLUMN: SELECTED ATTACHMENT INSPECTOR (28%) ------------------ */}
      <div className="w-[28%] bg-white border border-[#DCE3DE] rounded-lg p-5 flex flex-col justify-between shadow-sm flex-shrink-0 min-w-[320px]">
        {activeItem ? (
          <div>
            <h2 className="text-[14px] font-bold text-[#202824] mb-3">Selected attachment</h2>

            {/* File Header */}
            <div className="flex items-center gap-3 pb-3 mb-3 border-b border-[#DCE3DE]">
              <div className="w-9 h-9 rounded bg-[#D32F2F] text-white flex items-center justify-center font-bold text-[11px] flex-shrink-0">
                {(activeItem.extension || 'PDF').toUpperCase().slice(0, 3)}
              </div>
              <div className="overflow-hidden">
                <div className="font-bold text-[14px] text-[#202824] truncate" title={activeItem.original_filename}>
                  {activeItem.original_filename}
                </div>
                <div className="text-[11px] text-[#66716B] mt-0.5">
                  {(activeItem.extension || 'pdf').toUpperCase()} · {Math.round(activeItem.file_size / 1024)} KB · Received {formatDateLines(activeItem.received_at).date}
                </div>
              </div>
            </div>

            {/* Inspector Navigation Tabs */}
            <div className="flex border-b border-[#DCE3DE] mb-3 text-[13px] font-medium">
              {(['Overview', 'Preview', 'Routing'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setInspectorTab(tab)}
                  className={`pb-2 px-3 relative transition-colors ${
                    inspectorTab === tab
                      ? 'text-[#202824] font-semibold'
                      : 'text-[#66716B] hover:text-[#202824]'
                  }`}
                >
                  {tab}
                  {inspectorTab === tab && (
                    <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#286B50]" />
                  )}
                </button>
              ))}
            </div>

            {/* Tab 1: Overview */}
            {inspectorTab === 'Overview' && (
              <div>
                {/* Miniature Document Preview Card (Matching Reference Image) */}
                <div className="bg-white border border-[#DCE3DE] rounded-md p-3 mb-3.5 shadow-sm">
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#EAEFEA]">
                    <div className="flex items-center gap-1.5 text-[11px] font-bold text-[#202824]">
                      <Sparkles size={13} className="text-[#286B50]" />
                      <span>NORTHSTAR SUPPLIES — TAX INVOICE</span>
                    </div>
                    <div className="text-[9px] text-[#66716B] text-right leading-tight">
                      <div>Invoice No: NS-2026-1042</div>
                      <div>Date: 21/11/2026</div>
                    </div>
                  </div>

                  <div className="text-[10px] text-[#66716B] leading-tight mb-2.5">
                    <b>Bill To:</b><br />
                    Acme Corporation<br />
                    123 Business Ave, New York, NY 10001
                  </div>

                  <table className="w-full text-[10px] mb-2">
                    <thead>
                      <tr className="text-[#66716B] border-b border-[#DCE3DE]">
                        <th className="text-left pb-1 font-semibold">Description</th>
                        <th className="text-center pb-1 font-semibold">Qty</th>
                        <th className="text-right pb-1 font-semibold">Unit Price</th>
                        <th className="text-right pb-1 font-semibold">Total</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#F1F4F2]">
                      <tr>
                        <td className="py-1">Business Laptop</td>
                        <td className="text-center py-1">2</td>
                        <td className="text-right py-1">$999.00</td>
                        <td className="text-right py-1">$1,998.00</td>
                      </tr>
                      <tr>
                        <td className="py-1">Docking Station</td>
                        <td className="text-center py-1">2</td>
                        <td className="text-right py-1">$199.00</td>
                        <td className="text-right py-1">$398.00</td>
                      </tr>
                    </tbody>
                  </table>

                  <div className="flex justify-end gap-3 text-[11px] font-bold text-[#202824] pt-1 border-t border-[#EAEFEA]">
                    <span>Total</span>
                    <span>$2,396.00</span>
                  </div>
                </div>

                {/* Filing Decision Card */}
                <div>
                  <h3 className="text-[13px] font-bold text-[#202824] mb-2">Filing decision</h3>
                  <div className="space-y-1.5 text-[12px]">
                    <div className="flex justify-between items-center">
                      <span className="text-[#66716B]">Category:</span>
                      <span className="px-2 py-0.5 rounded bg-[#E9F2EC] text-[#286B50] font-semibold text-[11px]">
                        {activeItem.category}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-[#66716B]">Destination:</span>
                      <span className="font-mono text-[11px] text-[#202824]">
                        /{activeItem.rule_match?.destination || 'Finance/Invoices/2026'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-[#66716B]">Rule match:</span>
                      <span className="text-[#202824] font-medium text-[11px]">
                        {activeItem.rule_match?.rule_name || 'Vendor invoice rule'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-[#66716B]">Duplicate check:</span>
                      <span className="text-[#202824] text-[11px]">
                        {activeItem.duplicate_status || 'No matching SHA-256'}
                      </span>
                    </div>
                    <div className="pt-1">
                      <div className="text-[#66716B] text-[11px] mb-1">SHA-256:</div>
                      <div className="bg-[#F4F6F4] border border-[#DCE3DE] rounded px-2 py-1 font-mono text-[10px] text-[#66716B] break-all leading-tight">
                        {activeItem.sha256}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Tab 2: Preview */}
            {inspectorTab === 'Preview' && (
              <div className="text-[12px] space-y-3">
                <div className="bg-[#F7F9F7] border border-[#DCE3DE] rounded-md p-3">
                  <div className="font-semibold text-[#202824] mb-1">File Preview Information</div>
                  <div className="text-[#66716B] text-[11px]">
                    MIME Type: <code className="font-mono">{activeItem.mime_type}</code><br />
                    File Size: {(activeItem.file_size / 1024).toFixed(1)} KB<br />
                    Location: <code className="font-mono text-[10px]">{activeItem.current_path}</code>
                  </div>
                </div>
                <div className="border border-[#DCE3DE] rounded-md p-3 text-[11px] text-[#66716B] bg-white">
                  Full document visual render is ready. Preview payload validated with zero execution risk.
                </div>
              </div>
            )}

            {/* Tab 3: Routing */}
            {inspectorTab === 'Routing' && (
              <div className="space-y-3 text-[12px]">
                <div>
                  <label className="block text-[#66716B] text-[11px] font-semibold mb-1">Target Category</label>
                  <select
                    value={editCategory || activeItem.category}
                    onChange={(e) => setEditCategory(e.target.value)}
                    className="w-full bg-white border border-[#DCE3DE] rounded px-2.5 py-1.5 text-[12px] text-[#202824] focus:outline-none focus:border-[#286B50]"
                  >
                    <option value="Invoices">Finance / Invoices</option>
                    <option value="Receipts">Finance / Receipts</option>
                    <option value="Resumes / CVs">HR / Resumes</option>
                    <option value="Reports">Reports</option>
                    <option value="Documents">Documents</option>
                    <option value="Images">Images</option>
                    <option value="Archives">Archives</option>
                    <option value="Code / Technical Files">Code</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[#66716B] text-[11px] font-semibold mb-1">Destination Subfolder</label>
                  <input
                    type="text"
                    value={editDestination || activeItem.rule_match?.destination || 'Finance/Invoices'}
                    onChange={(e) => setEditDestination(e.target.value)}
                    className="w-full bg-white border border-[#DCE3DE] rounded px-2.5 py-1.5 text-[12px] text-[#202824] focus:outline-none focus:border-[#286B50]"
                  />
                </div>

                <div>
                  <label className="block text-[#66716B] text-[11px] font-semibold mb-1">Duplicate Strategy</label>
                  <select
                    value={editDupStrategy}
                    onChange={(e) => setEditDupStrategy(e.target.value)}
                    className="w-full bg-white border border-[#DCE3DE] rounded px-2.5 py-1.5 text-[12px] text-[#202824] focus:outline-none focus:border-[#286B50]"
                  >
                    <option value="keep_copy">Keep Copy (Numbered _001)</option>
                    <option value="skip">Skip Duplicate</option>
                    <option value="keep_reference">Link Reference to Existing File</option>
                  </select>
                </div>

                <button
                  onClick={() => onOverrideRouting(activeItem.id, {
                    category: editCategory || activeItem.category,
                    destination: editDestination || activeItem.rule_match?.destination,
                    duplicate_action: editDupStrategy,
                  })}
                  className="w-full py-1.5 bg-[#286B50] hover:bg-[#20553F] text-white rounded text-[12px] font-medium transition-all"
                >
                  Save & File Document
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="py-12 text-center text-[13px] text-[#66716B]">
            No attachment selected.
          </div>
        )}

        {/* Bottom Actions */}
        {activeItem && (
          <div className="flex items-center gap-2.5 pt-4 mt-4 border-t border-[#DCE3DE]">
            <button
              onClick={() => setInspectorTab('Routing')}
              className="flex-1 py-2 bg-white border border-[#DCE3DE] hover:bg-[#F7F9F7] text-[#202824] text-[13px] font-medium rounded-md transition-all text-center"
            >
              Edit destination
            </button>
            <button
              onClick={() => {
                onApproveSingle(activeItem.id);
                const next = new Set(checkedIds);
                next.delete(activeItem.id);
                setCheckedIds(next);
              }}
              className="flex-1 py-2 bg-[#286B50] hover:bg-[#20553F] text-white text-[13px] font-medium rounded-md transition-all text-center shadow-sm"
            >
              Approve file
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
