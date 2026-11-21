import React, { useState, useEffect } from 'react';
import { 
  History, Search, Download, Filter, CheckCircle2, 
  RotateCcw, AlertCircle, RefreshCw, FileText 
} from 'lucide-react';
import { OperationRecord } from '../types';

export const HistoryView: React.FC = () => {
  const [operations, setOperations] = useState<OperationRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('All');
  const [typeFilter, setTypeFilter] = useState<string>('All');

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (statusFilter !== 'All') params.append('status', statusFilter);
      if (typeFilter !== 'All') params.append('operation_type', typeFilter);

      const res = await fetch(`/api/history?${params.toString()}`);
      const data = await res.json();
      setOperations(data.operations || []);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [search, statusFilter, typeFilter]);

  const handleExportCSV = () => {
    window.open('/api/history/export', '_blank');
  };

  const getStatusBadge = (status: string) => {
    if (status === 'Success') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-[#EBF7F0] text-[#1E5638] border border-[#A3D9B8]">
          <CheckCircle2 className="w-3 h-3" /> Success
        </span>
      );
    }
    if (status === 'Rolled Back') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-[#FFFBEB] text-[#B45309] border border-[#FDE68A]">
          <RotateCcw className="w-3 h-3" /> Rolled Back
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-[#FDF2F2] text-[#991B1B] border border-[#F87171]">
        <AlertCircle className="w-3 h-3" /> {status}
      </span>
    );
  };

  return (
    <div className="flex-1 overflow-y-auto px-8 py-6 bg-[#F4F6F4]">
      {/* Title */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-[24px] font-bold text-[#202824] tracking-tight flex items-center gap-2">
            <History className="w-6 h-6 text-[#286B50]" />
            Operation Audit Trail
          </h1>
          <p className="text-[13px] text-[#66716B] mt-0.5">
            Immutable log of all attachment extractions, filing decisions, duplicates, and rollback operations.
          </p>
        </div>
        <button
          onClick={handleExportCSV}
          className="flex items-center gap-1.5 px-3 py-1.5 text-[12px] font-medium text-white bg-[#286B50] hover:bg-[#1E5638] rounded-md transition-colors shadow-sm"
        >
          <Download className="w-3.5 h-3.5" />
          Export Audit Log (CSV)
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white border border-[#DCE3DE] rounded-lg p-4 mb-6 flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[280px]">
          <Search className="w-4 h-4 text-[#8A948E] absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search filenames, paths, senders or SHA-256..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-[13px] text-[#202824] bg-white border border-[#DCE3DE] rounded-md focus:outline-none focus:border-[#286B50]"
          />
        </div>
        <div className="flex items-center gap-2">
          <label className="text-[12px] font-medium text-[#66716B]">Status:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="py-1.5 px-2.5 text-[12px] text-[#202824] bg-white border border-[#DCE3DE] rounded-md focus:outline-none focus:border-[#286B50]"
          >
            <option value="All">All Statuses</option>
            <option value="Success">Success</option>
            <option value="Rolled Back">Rolled Back</option>
            <option value="Failed">Failed</option>
          </select>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-[12px] font-medium text-[#66716B]">Action:</label>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="py-1.5 px-2.5 text-[12px] text-[#202824] bg-white border border-[#DCE3DE] rounded-md focus:outline-none focus:border-[#286B50]"
          >
            <option value="All">All Actions</option>
            <option value="Organize">Organize</option>
            <option value="Skip">Skip</option>
            <option value="Rollback">Rollback</option>
          </select>
        </div>
      </div>

      {/* Operations Table */}
      <div className="bg-white border border-[#DCE3DE] rounded-lg overflow-hidden shadow-sm">
        <div className="px-5 py-3 border-b border-[#DCE3DE] bg-[#F7F9F7] flex items-center justify-between">
          <span className="text-[12px] font-semibold text-[#202824]">
            Recorded Operations ({operations.length})
          </span>
          <button
            onClick={fetchHistory}
            className="text-[11px] text-[#286B50] hover:underline flex items-center gap-1"
          >
            <RefreshCw className="w-3 h-3" /> Refresh
          </button>
        </div>

        {loading ? (
          <div className="py-16 text-center text-[#66716B] text-[13px]">
            <RefreshCw className="w-5 h-5 text-[#286B50] animate-spin mx-auto mb-2" />
            Loading audit trail...
          </div>
        ) : operations.length === 0 ? (
          <div className="py-16 text-center text-[#66716B]">
            <FileText className="w-10 h-10 text-[#8A948E] mx-auto mb-2 opacity-50" />
            <p className="text-[14px] font-medium text-[#202824]">No operation events found</p>
            <p className="text-[12px] text-[#8A948E] mt-1">
              Events will record as you approve, skip or undo attachments.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-[12px]">
              <thead className="bg-[#F7F9F7] border-b border-[#DCE3DE] text-[#66716B] font-medium">
                <tr>
                  <th className="py-2.5 px-4">Timestamp</th>
                  <th className="py-2.5 px-4">Action</th>
                  <th className="py-2.5 px-4">Attachment</th>
                  <th className="py-2.5 px-4">Target Destination</th>
                  <th className="py-2.5 px-4">Status</th>
                  <th className="py-2.5 px-4">Integrity Hash</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#DCE3DE]">
                {operations.map((op) => (
                  <tr key={op.id} className="hover:bg-[#F1F6F2] transition-colors">
                    <td className="py-3 px-4 font-mono text-[11px] text-[#66716B] whitespace-nowrap">
                      {op.timestamp ? op.timestamp.replace('T', ' ').slice(0, 19) : '—'}
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-semibold text-[#202824]">
                        {op.operation_type}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-medium text-[#202824] leading-snug">
                        {op.original_filename || op.final_filename || 'Unknown'}
                      </div>
                      <div className="text-[11px] text-[#8A948E]">
                        {op.sender || 'Direct import'}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-mono text-[11px] text-[#286B50]">
                        {op.destination_path || '—'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {getStatusBadge(op.status)}
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-mono text-[10px] text-[#66716B] bg-[#F4F6F4] px-1.5 py-0.5 rounded border border-[#DCE3DE]">
                        {op.sha256 ? `${op.sha256.slice(0, 12)}...` : '—'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
