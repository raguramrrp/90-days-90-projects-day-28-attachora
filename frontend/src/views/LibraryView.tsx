import React, { useState, useEffect } from 'react';
import { 
  FolderCheck, Search, Undo2, ArrowUpRight, CheckCircle2, 
  FileText, ShieldCheck, AlertCircle, RefreshCw 
} from 'lucide-react';
import { Attachment } from '../types';

interface LibraryViewProps {
  onRefreshSummary: () => void;
}

export const LibraryView: React.FC<LibraryViewProps> = ({ onRefreshSummary }) => {
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [undoingId, setUndoingId] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const fetchOrganized = async () => {
    try {
      setLoading(true);
      const res = await fetch(`/api/attachments?status=Organized&search=${encodeURIComponent(search)}&category=${selectedCategory}`);
      const data = await res.json();
      setAttachments(data.attachments || []);
    } catch (err) {
      console.error('Failed to load library:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrganized();
  }, [search, selectedCategory]);

  const handleUndo = async (id: number, filename: string) => {
    if (!confirm(`Undo filing and restore "${filename}" back to pending queue?`)) return;
    try {
      setUndoingId(id);
      const res = await fetch(`/api/attachments/${id}/undo`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setFeedback({ message: `Successfully restored ${filename} to queue.`, type: 'success' });
        fetchOrganized();
        onRefreshSummary();
      } else {
        setFeedback({ message: data.error || 'Failed to undo filing operation.', type: 'error' });
      }
    } catch (err) {
      setFeedback({ message: 'Error executing rollback operation.', type: 'error' });
    } finally {
      setUndoingId(null);
      setTimeout(() => setFeedback(null), 4000);
    }
  };

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFileBadge = (ext: string) => {
    const cleanExt = ext.replace('.', '').toUpperCase();
    let bg = 'bg-[#DC2626]';
    if (['DOC', 'DOCX'].includes(cleanExt)) bg = 'bg-[#2563EB]';
    else if (['XLS', 'XLSX', 'CSV'].includes(cleanExt)) bg = 'bg-[#16A34A]';
    else if (['ZIP', 'RAR', '7Z', 'TAR'].includes(cleanExt)) bg = 'bg-[#D97706]';
    else if (['TXT', 'LOG', 'JSON'].includes(cleanExt)) bg = 'bg-[#4B5563]';

    return (
      <span className={`inline-flex items-center justify-center w-6 h-6 rounded text-[10px] font-bold text-white shrink-0 ${bg}`}>
        {cleanExt.slice(0, 3)}
      </span>
    );
  };

  return (
    <div className="flex-1 overflow-y-auto px-8 py-6 bg-[#F4F6F4]">
      {/* Title */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-[24px] font-bold text-[#202824] tracking-tight flex items-center gap-2">
            <FolderCheck className="w-6 h-6 text-[#286B50]" />
            Organized Library
          </h1>
          <p className="text-[13px] text-[#66716B] mt-0.5">
            Verified, safely categorized files filed into structured disk directories.
          </p>
        </div>
        <button
          onClick={fetchOrganized}
          className="flex items-center gap-1.5 px-3 py-1.5 text-[12px] font-medium text-[#202824] bg-white border border-[#DCE3DE] rounded-md hover:bg-[#F7F9F7] transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5 text-[#66716B]" />
          Refresh
        </button>
      </div>

      {feedback && (
        <div className={`mb-4 px-4 py-3 rounded-md text-[13px] flex items-center gap-2 ${
          feedback.type === 'success' ? 'bg-[#EBF7F0] text-[#1E5638] border border-[#A3D9B8]' : 'bg-[#FDF2F2] text-[#991B1B] border border-[#F87171]'
        }`}>
          {feedback.type === 'success' ? <CheckCircle2 className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
          {feedback.message}
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="bg-white border border-[#DCE3DE] rounded-lg p-4 mb-6 flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[280px]">
          <Search className="w-4 h-4 text-[#8A948E] absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search filed documents, categories, paths or SHA-256..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-[13px] text-[#202824] bg-white border border-[#DCE3DE] rounded-md focus:outline-none focus:border-[#286B50]"
          />
        </div>
        <div className="flex items-center gap-2">
          <label className="text-[12px] font-medium text-[#66716B]">Category:</label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="py-1.5 px-2.5 text-[12px] text-[#202824] bg-white border border-[#DCE3DE] rounded-md focus:outline-none focus:border-[#286B50]"
          >
            <option value="All">All Categories</option>
            <option value="Finance / Invoices">Finance / Invoices</option>
            <option value="Finance / Receipts">Finance / Receipts</option>
            <option value="Documents">Documents</option>
            <option value="Contracts / Legal">Contracts / Legal</option>
            <option value="Images">Images</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white border border-[#DCE3DE] rounded-lg overflow-hidden shadow-sm">
        <div className="px-5 py-3 border-b border-[#DCE3DE] bg-[#F7F9F7] flex items-center justify-between">
          <span className="text-[12px] font-semibold text-[#202824]">
            Organized Documents ({attachments.length})
          </span>
          <span className="text-[11px] text-[#8A948E]">
            Stored in: <code className="bg-[#EAEFEA] px-1.5 py-0.5 rounded text-[#286B50] font-mono">organized/</code>
          </span>
        </div>

        {loading ? (
          <div className="py-16 text-center text-[#66716B] text-[13px]">
            <RefreshCw className="w-5 h-5 text-[#286B50] animate-spin mx-auto mb-2" />
            Loading organized files...
          </div>
        ) : attachments.length === 0 ? (
          <div className="py-16 text-center text-[#66716B]">
            <FolderCheck className="w-10 h-10 text-[#8A948E] mx-auto mb-2 opacity-50" />
            <p className="text-[14px] font-medium text-[#202824]">No organized attachments in library yet</p>
            <p className="text-[12px] text-[#8A948E] mt-1">
              Go to the Queue view and click "Approve and file" on pending documents.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-[12px]">
              <thead className="bg-[#F7F9F7] border-b border-[#DCE3DE] text-[#66716B] font-medium">
                <tr>
                  <th className="py-2.5 px-4">Attachment / Destination</th>
                  <th className="py-2.5 px-4">Category</th>
                  <th className="py-2.5 px-4">Sender / Email</th>
                  <th className="py-2.5 px-4">Size</th>
                  <th className="py-2.5 px-4">Integrity Hash</th>
                  <th className="py-2.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#DCE3DE]">
                {attachments.map((att) => (
                  <tr key={att.id} className="hover:bg-[#F1F6F2] transition-colors">
                    <td className="py-3 px-4">
                      <div className="flex items-start gap-2.5">
                        {getFileBadge(att.extension)}
                        <div>
                          <div className="font-semibold text-[#202824] leading-snug">
                            {att.original_filename}
                          </div>
                          <div className="text-[11px] text-[#286B50] font-mono mt-0.5 flex items-center gap-1">
                            <span className="text-[#8A948E]">Target:</span>
                            {att.current_path.replace(/\\/g, '/')}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-block px-2 py-0.5 text-[11px] font-medium rounded bg-[#EBF7F0] text-[#1E5638] border border-[#A3D9B8]">
                        {att.category}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-medium text-[#202824]">{att.sender || 'Unknown'}</div>
                      <div className="text-[11px] text-[#8A948E]">{att.subject || 'No Subject'}</div>
                    </td>
                    <td className="py-3 px-4 text-[#66716B] font-mono">
                      {formatSize(att.file_size)}
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-mono text-[10px] text-[#66716B] bg-[#F4F6F4] px-1.5 py-0.5 rounded border border-[#DCE3DE]" title={att.sha256}>
                        {att.sha256.slice(0, 12)}...
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleUndo(att.id, att.original_filename)}
                        disabled={undoingId === att.id}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-medium text-[#B91C1C] bg-white border border-[#FCA5A5] rounded hover:bg-[#FEF2F2] transition-colors disabled:opacity-50"
                        title="Rollback this filing and return to queue"
                      >
                        <Undo2 className="w-3 h-3" />
                        {undoingId === att.id ? 'Restoring...' : 'Undo'}
                      </button>
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
