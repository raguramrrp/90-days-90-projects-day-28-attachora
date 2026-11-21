import React, { useState, useEffect } from 'react';
import { NavigationRail } from './components/NavigationRail';
import { TopHeader } from './components/TopHeader';
import { QueueView } from './views/QueueView';
import { RulesView } from './views/RulesView';
import { LibraryView } from './views/LibraryView';
import { MailboxView } from './views/MailboxView';
import { IntegrityView } from './views/IntegrityView';
import { HistoryView } from './views/HistoryView';
import { AnalyticsView } from './views/AnalyticsView';
import { SettingsView } from './views/SettingsView';
import { Attachment, SummaryMetrics } from './types';
import { Check, CheckCircle2, AlertCircle, X, Download, RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const getInitialPage = () => {
    try {
      const params = new URLSearchParams(window.location.search);
      const p = params.get('page');
      if (p) {
        const valid = ['Queue', 'Mailbox', 'Integrity', 'Rules', 'Library', 'History', 'Analytics', 'Settings'];
        const match = valid.find((v) => v.toLowerCase() === p.toLowerCase());
        if (match) return match;
      }
    } catch {}
    return 'Queue';
  };

  const [activePage, setActivePage] = useState<string>(getInitialPage);

  const handleSelectPage = (page: string) => {
    setActivePage(page);
    try {
      const url = new URL(window.location.href);
      url.searchParams.set('page', page);
      window.history.replaceState({}, '', url.toString());
    } catch {}
  };
  const [summary, setSummary] = useState<SummaryMetrics | null>(null);
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [selectedRowId, setSelectedRowId] = useState<number | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const [showImportModal, setShowImportModal] = useState<boolean>(false);
  const [importing, setImporting] = useState<boolean>(false);

  const showNotification = (message: string, type: 'success' | 'error' = 'success') => {
    setNotification({ message, type });
    setTimeout(() => {
      setNotification(null);
    }, 4000);
  };

  const fetchSummary = async () => {
    try {
      const res = await fetch('/api/summary');
      if (res.ok) {
        const data = await res.json();
        setSummary(data);
      }
    } catch (err) {
      console.error('Error fetching summary:', err);
    }
  };

  const fetchAttachments = async (justOrganizedId?: number) => {
    try {
      const res = await fetch('/api/attachments');
      if (res.ok) {
        const data = await res.json();
        const attList: Attachment[] = data.attachments || [];
        setAttachments(attList);
        const unfiled = attList.filter((a) => a.status !== 'Organized' && a.status !== 'Skipped');
        if (justOrganizedId && selectedRowId === justOrganizedId) {
          setSelectedRowId(unfiled.length > 0 ? unfiled[0].id : null);
        } else if ((!selectedRowId || !attList.some((a) => a.id === selectedRowId)) && unfiled.length > 0) {
          setSelectedRowId(unfiled[0].id);
        }
      }
    } catch (err) {
      console.error('Error fetching attachments:', err);
    } finally {
      setLoading(false);
    }
  };

  const refreshAllData = async (justOrganizedId?: number) => {
    await Promise.all([fetchSummary(), fetchAttachments(justOrganizedId)]);
  };

  useEffect(() => {
    refreshAllData();
  }, []);

  // Single Approve
  const handleApproveSingle = async (id: number) => {
    try {
      const res = await fetch(`/api/attachments/${id}/approve`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        showNotification(`Successfully approved & filed "${data.final_filename || 'document'}" to ${data.target_path || 'library'}.`);
        refreshAllData(id);
      } else {
        showNotification(data.error || 'Failed to file attachment.', 'error');
      }
    } catch (err) {
      showNotification('Error processing approval request.', 'error');
    }
  };

  // Bulk Approve
  const handleApproveBulk = async (ids: number[]) => {
    try {
      const res = await fetch('/api/attachments/bulk-approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids }),
      });
      const data = await res.json();
      if (data.success) {
        showNotification(`Batch processed: ${data.count} attachments organized successfully into library.`);
        refreshAllData(ids[0]);
      } else {
        showNotification('Bulk approval failed.', 'error');
      }
    } catch (err) {
      showNotification('Error processing bulk approval.', 'error');
    }
  };

  // Bulk Skip
  const handleSkipBulk = async (ids: number[]) => {
    try {
      const res = await fetch('/api/attachments/bulk-skip', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids }),
      });
      const data = await res.json();
      if (data.success) {
        showNotification(`Marked ${data.count} attachments as skipped.`);
        refreshAllData();
      } else {
        showNotification('Bulk skip failed.', 'error');
      }
    } catch (err) {
      showNotification('Error processing bulk skip.', 'error');
    }
  };

  // Single Undo
  const handleUndoSingle = async (id: number) => {
    try {
      const res = await fetch(`/api/attachments/${id}/undo`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        showNotification(`Restored attachment #${id} back to staging.`);
        refreshAllData();
      } else {
        showNotification(data.error || 'Failed to undo filing operation.', 'error');
      }
    } catch (err) {
      showNotification('Error executing rollback.', 'error');
    }
  };

  // Override Routing
  const handleOverrideRouting = async (id: number, overrideData: any) => {
    try {
      const res = await fetch(`/api/attachments/${id}/override`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(overrideData),
      });
      const data = await res.json();
      if (data.success) {
        showNotification(`Updated routing destination for attachment #${id}.`);
        refreshAllData();
      } else {
        showNotification(data.error || 'Failed to update destination.', 'error');
      }
    } catch (err) {
      showNotification('Error updating routing destination.', 'error');
    }
  };

  // Quick Ingestion Modal Handler
  const handleTriggerSampleSync = async () => {
    try {
      setImporting(true);
      const res = await fetch('/api/sync', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        showNotification(`Imported ${data.attachments_detected} attachments from ${data.emails_scanned} sample messages.`);
        setShowImportModal(false);
        setActivePage('Queue');
        refreshAllData();
      } else {
        showNotification(data.error || 'Import failed.', 'error');
      }
    } catch (err) {
      showNotification('Error triggering email scan.', 'error');
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#F4F6F4] font-sans text-[#202824] antialiased">
      {/* 1. Left Narrow Navigation Rail (76px) */}
      <NavigationRail
        activePage={activePage}
        onSelectPage={handleSelectPage}
      />

      {/* Main Container */}
      <div className="flex flex-col flex-1 h-screen overflow-hidden">
        {/* 2. Top Header Bar */}
        <TopHeader
          activePage={activePage}
          onSelectPage={handleSelectPage}
          onImportClick={() => setShowImportModal(true)}
          mailboxStatus="Local mailbox"
        />

        {/* Global Notification Toast */}
        {notification && (
          <div
            className={`fixed top-4 right-6 z-50 px-4 py-2.5 rounded-lg shadow-lg border text-[13px] font-medium flex items-center gap-2 animate-in fade-in slide-in-from-top-2 duration-200 ${
              notification.type === 'success'
                ? 'bg-[#EBF7F0] text-[#1E5638] border-[#A3D9B8]'
                : 'bg-[#FDF2F2] text-[#991B1B] border-[#F87171]'
            }`}
          >
            {notification.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-[#286B50] shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-[#991B1B] shrink-0" />
            )}
            <span>{notification.message}</span>
            <button
              onClick={() => setNotification(null)}
              className="ml-2 hover:opacity-75 transition-opacity"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* 3. Active Workspace View */}
        <main className="flex-1 overflow-hidden flex flex-col">
          {activePage === 'Queue' && (
            <QueueView
              attachments={attachments}
              summary={summary}
              selectedRowId={selectedRowId}
              onSelectRow={(id) => setSelectedRowId(id)}
              onApproveSingle={handleApproveSingle}
              onApproveBulk={handleApproveBulk}
              onSkipBulk={handleSkipBulk}
              onUndoSingle={handleUndoSingle}
              onOverrideRouting={handleOverrideRouting}
              onRefresh={refreshAllData}
            />
          )}

          {activePage === 'Rules' && <RulesView />}

          {activePage === 'Library' && (
            <LibraryView onRefreshSummary={refreshAllData} />
          )}

          {activePage === 'Mailbox' && (
            <MailboxView
              onRefreshSummary={refreshAllData}
              onNavigateToQueue={() => setActivePage('Queue')}
            />
          )}

          {activePage === 'Integrity' && <IntegrityView />}

          {activePage === 'History' && <HistoryView />}

          {activePage === 'Analytics' && <AnalyticsView />}

          {activePage === 'Settings' && <SettingsView />}
        </main>

        {/* 4. Bottom Status Bar matching reference design */}
        <footer className="h-[28px] bg-white border-t border-[#DCE3DE] px-4 flex items-center justify-between text-[11px] text-[#66716B] select-none flex-shrink-0 z-10">
          <div className="flex items-center gap-1.5 font-medium text-[#202824]">
            <Check size={13} className="text-[#286B50] stroke-[2.5]" />
            <span>Local storage · {attachments.length} attachments indexed · All changes saved</span>
          </div>
          <div className="flex items-center gap-4 text-[#8A948E]">
            <span>SQLite WAL Mode: Active</span>
            <span>Zero-Trust SHA-256 Engine</span>
          </div>
        </footer>
      </div>

      {/* Quick Ingestion Modal */}
      {showImportModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="bg-white rounded-lg shadow-xl border border-[#DCE3DE] w-full max-w-md p-6 relative">
            <button
              onClick={() => setShowImportModal(false)}
              className="absolute top-4 right-4 text-[#8A948E] hover:text-[#202824]"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2.5 text-[16px] font-bold text-[#202824] mb-2">
              <Download className="w-5 h-5 text-[#286B50]" />
              Import Email Attachments
            </div>

            <p className="text-[13px] text-[#66716B] leading-relaxed mb-5">
              Select an import method to ingest incoming messages into the classification workstation.
            </p>

            <div className="space-y-3">
              <button
                onClick={handleTriggerSampleSync}
                disabled={importing}
                className="w-full py-3 px-4 bg-[#286B50] hover:bg-[#1E5638] text-white text-[13px] font-semibold rounded-md shadow-sm flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                {importing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Scanning 12 Sample Test Emails...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    Scan 12 Sample Test Emails (Instant)
                  </>
                )}
              </button>

              <button
                onClick={() => {
                  setShowImportModal(false);
                  setActivePage('Mailbox');
                }}
                className="w-full py-2.5 px-4 bg-white hover:bg-[#F7F9F7] text-[#202824] text-[13px] font-semibold rounded-md border border-[#DCE3DE] transition-colors"
              >
                Configure IMAP Connection →
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
