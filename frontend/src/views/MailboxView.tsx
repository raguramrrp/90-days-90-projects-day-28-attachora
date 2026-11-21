import React, { useState } from 'react';
import { 
  Mail, Download, CheckCircle2, AlertCircle, RefreshCw, 
  Server, Shield, Folder, Key, Lock, FileCode, Check, Upload, ArrowRight 
} from 'lucide-react';

interface MailboxViewProps {
  onRefreshSummary: () => void;
  onNavigateToQueue: () => void;
}

export const MailboxView: React.FC<MailboxViewProps> = ({ onRefreshSummary, onNavigateToQueue }) => {
  const [syncing, setSyncing] = useState<boolean>(false);
  const [testing, setTesting] = useState<boolean>(false);
  const [uploading, setUploading] = useState<boolean>(false);

  const [syncResult, setSyncResult] = useState<{ emails_scanned: number; attachments_detected: number } | null>(null);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string; mailboxes?: string[] } | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Form states for IMAP settings
  const [imapServer, setImapServer] = useState<string>('imap.gmail.com');
  const [imapPort, setImapPort] = useState<number>(993);
  const [sslEnabled, setSslEnabled] = useState<boolean>(true);
  const [username, setUsername] = useState<string>('user@company.com');
  const [password, setPassword] = useState<string>('');
  const [folder, setFolder] = useState<string>('INBOX');
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  // 1. Sync bundled sample emails
  const handleSyncSample = async () => {
    try {
      setSyncing(true);
      setError(null);
      setSyncResult(null);

      const res = await fetch('/api/sync', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setSyncResult({
          emails_scanned: data.emails_scanned,
          attachments_detected: data.attachments_detected,
        });
        onRefreshSummary();
      } else {
        setError(data.error || 'Failed to sync sample emails.');
      }
    } catch (err) {
      setError('Network error while connecting to email source.');
    } finally {
      setSyncing(false);
    }
  };

  // 2. Real IMAP Connection Test
  const handleTestConnection = async () => {
    if (!imapServer || !username || !password) {
      setError('Please provide host, username, and password / app password to test connection.');
      return;
    }
    try {
      setTesting(true);
      setError(null);
      setTestResult(null);

      const res = await fetch('/api/mailbox/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          host: imapServer,
          port: imapPort,
          username,
          password,
          use_ssl: sslEnabled,
        }),
      });
      const data = await res.json();
      if (data.success) {
        setTestResult({
          success: true,
          message: data.message || 'Connection successful!',
          mailboxes: data.mailboxes || [],
        });
      } else {
        setTestResult({
          success: false,
          message: data.error || data.message || 'Connection failed.',
        });
      }
    } catch (err) {
      setTestResult({
        success: false,
        message: 'Could not contact IMAP host. Please check network and server hostname.',
      });
    } finally {
      setTesting(false);
    }
  };

  // 3. Save Account & Trigger Real IMAP Sync
  const handleSaveAndSyncReal = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      setSyncing(true);
      // Save profile
      const saveRes = await fetch('/api/mailbox/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          account_email: username,
          imap_host: imapServer,
          imap_port: imapPort,
          mailbox: folder,
          password,
        }),
      });
      const saveData = await saveRes.json();
      if (!saveData.success) {
        setError(saveData.error || 'Failed to save account configuration.');
        setSyncing(false);
        return;
      }
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);

      // Perform real sync if password provided
      if (password) {
        const syncRes = await fetch('/api/mailbox/sync-real', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            account_id: saveData.account_id,
            password,
          }),
        });
        const realSyncData = await syncRes.json();
        if (realSyncData.success) {
          setSyncResult({
            emails_scanned: realSyncData.messages_scanned || 0,
            attachments_detected: realSyncData.attachments_detected || 0,
          });
          onRefreshSummary();
        } else {
          setError(realSyncData.error || 'Real IMAP sync failed.');
        }
      }
    } catch (err) {
      setError('Error communicating with IMAP server.');
    } finally {
      setSyncing(false);
    }
  };

  // 4. Upload raw real .EML file
  const handleEmlUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setError(null);

      const reader = new FileReader();
      reader.onload = async () => {
        try {
          const base64Content = (reader.result as string).split(',')[1];
          const res = await fetch('/api/upload-eml', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              filename: file.name,
              content_b64: base64Content,
            }),
          });
          const data = await res.json();
          if (data.success) {
            setSyncResult({
              emails_scanned: 1,
              attachments_detected: data.attachments_count || 0,
            });
            onRefreshSummary();
          } else {
            setError(data.error || 'Failed to parse uploaded .eml file.');
          }
        } catch (uploadErr) {
          setError('Error uploading email file.');
        } finally {
          setUploading(false);
        }
      };
      reader.readAsDataURL(file);
    } catch (err) {
      setError('Failed to read file.');
      setUploading(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto px-8 py-6 bg-[#F4F6F4]">
      {/* Title */}
      <div className="mb-6">
        <h1 className="text-[24px] font-bold text-[#202824] tracking-tight flex items-center gap-2">
          <Mail className="w-6 h-6 text-[#286B50]" />
          Email Connection & Ingestion
        </h1>
        <p className="text-[13px] text-[#66716B] mt-0.5">
          Configure real IMAP connections, upload custom .EML email files, or test with bundled sample datasets.
        </p>
      </div>

      {/* Sync Status Banner */}
      {syncResult && (
        <div className="mb-6 p-4 rounded-lg bg-[#EBF7F0] border border-[#A3D9B8] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-[#286B50] shrink-0" />
            <div>
              <div className="text-[14px] font-semibold text-[#1E5638]">
                Email Ingestion Completed Successfully
              </div>
              <div className="text-[12px] text-[#286B50] mt-0.5">
                Scanned {syncResult.emails_scanned} emails and extracted {syncResult.attachments_detected} valid attachments into the processing queue.
              </div>
            </div>
          </div>
          <button
            onClick={onNavigateToQueue}
            className="px-3.5 py-1.5 text-[12px] font-semibold text-white bg-[#286B50] hover:bg-[#1E5638] rounded-md transition-colors shadow-sm"
          >
            View in Queue →
          </button>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-[#FDF2F2] border border-[#F87171] text-[13px] text-[#991B1B] flex items-center gap-2">
          <AlertCircle className="w-5 h-5 shrink-0" />
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Quick Ingestion & EML Upload */}
        <div className="lg:col-span-1 space-y-6">
          {/* Quick Dataset Ingestion */}
          <div className="bg-white border border-[#DCE3DE] rounded-lg p-5 shadow-sm">
            <div className="flex items-center gap-2 text-[15px] font-bold text-[#202824] mb-2">
              <Download className="w-4 h-4 text-[#286B50]" />
              Quick Dataset Ingestion
            </div>
            <p className="text-[12px] text-[#66716B] leading-relaxed mb-4">
              Ingest the bundled repository of 12 realistic business test emails (Invoices, Receipts, NDAs, Code packages, and Zip files) to evaluate the extraction pipeline.
            </p>
            <button
              onClick={handleSyncSample}
              disabled={syncing}
              className="w-full py-2.5 px-4 bg-[#286B50] hover:bg-[#1E5638] text-white text-[13px] font-semibold rounded-md shadow-sm flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
            >
              {syncing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Scanning & Extracting...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  Import 12 Sample Test Emails
                </>
              )}
            </button>
            <div className="mt-3 text-[11px] text-[#8A948E] text-center">
              Source: <code className="bg-[#F4F6F4] px-1 py-0.5 rounded text-[#286B50]">data/sample_emails/</code>
            </div>
          </div>

          {/* Upload Real .EML File */}
          <div className="bg-white border border-[#DCE3DE] rounded-lg p-5 shadow-sm">
            <div className="flex items-center gap-2 text-[14px] font-bold text-[#202824] mb-2">
              <Upload className="w-4 h-4 text-[#286B50]" />
              Upload Real .EML Message
            </div>
            <p className="text-[12px] text-[#66716B] leading-relaxed mb-3">
              Drop or select any real saved email (.eml file) from your computer to extract and classify its attachments:
            </p>
            <label className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-[#DCE3DE] rounded-lg hover:border-[#286B50] bg-[#F7F9F7] cursor-pointer transition-colors">
              <Upload className="w-6 h-6 text-[#8A948E] mb-1" />
              <span className="text-[12px] font-medium text-[#202824]">
                {uploading ? 'Parsing attachments...' : 'Select .EML file'}
              </span>
              <span className="text-[10px] text-[#8A948E] mt-0.5">MIME & binary validation enforced</span>
              <input
                type="file"
                accept=".eml"
                onChange={handleEmlUpload}
                disabled={uploading}
                className="hidden"
              />
            </label>
          </div>

          {/* Ingestion Safeguards */}
          <div className="bg-white border border-[#DCE3DE] rounded-lg p-5 shadow-sm">
            <div className="flex items-center gap-2 text-[14px] font-bold text-[#202824] mb-2">
              <Shield className="w-4 h-4 text-[#286B50]" />
              Ingestion Safeguards
            </div>
            <ul className="text-[12px] text-[#66716B] space-y-2">
              <li className="flex items-start gap-2">
                <Check className="w-3.5 h-3.5 text-[#286B50] mt-0.5 shrink-0" />
                <span><strong>Read-Only IMAP:</strong> Emails are never deleted or modified in your inbox.</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="w-3.5 h-3.5 text-[#286B50] mt-0.5 shrink-0" />
                <span><strong>RAM-Only Secrets:</strong> Passwords held in encrypted volatile memory.</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="w-3.5 h-3.5 text-[#286B50] mt-0.5 shrink-0" />
                <span><strong>Path Traversal Defense:</strong> All attachment filenames sanitized.</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Right Column: Real IMAP Server Connection Profile */}
        <div className="lg:col-span-2">
          <div className="bg-white border border-[#DCE3DE] rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4 border-b border-[#DCE3DE] pb-3">
              <div>
                <h2 className="text-[16px] font-bold text-[#202824] flex items-center gap-2">
                  <Server className="w-4 h-4 text-[#286B50]" />
                  Real IMAP Server Connection Profile
                </h2>
                <p className="text-[12px] text-[#66716B]">
                  Connect to Gmail, Outlook, Yahoo, or corporate IMAP mailboxes with read-only TLS security.
                </p>
              </div>
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-semibold bg-[#EBF7F0] text-[#1E5638] border border-[#A3D9B8]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#16A34A] animate-pulse"></span>
                IMAP Ready
              </span>
            </div>

            {testResult && (
              <div className={`mb-4 p-3.5 rounded-lg text-[12px] border flex items-start gap-2.5 ${
                testResult.success
                  ? 'bg-[#EBF7F0] border-[#A3D9B8] text-[#1E5638]'
                  : 'bg-[#FDF2F2] border-[#F87171] text-[#991B1B]'
              }`}>
                {testResult.success ? <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" /> : <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />}
                <div>
                  <div className="font-semibold">{testResult.message}</div>
                  {testResult.mailboxes && testResult.mailboxes.length > 0 && (
                    <div className="mt-1 text-[11px] text-[#286B50]">
                      Available Mailbox Folders: {testResult.mailboxes.slice(0, 6).join(', ')}
                    </div>
                  )}
                </div>
              </div>
            )}

            <form onSubmit={handleSaveAndSyncReal} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[12px] font-medium text-[#202824] mb-1">
                    IMAP Host Server
                  </label>
                  <input
                    type="text"
                    value={imapServer}
                    onChange={(e) => setImapServer(e.target.value)}
                    placeholder="e.g. imap.gmail.com or outlook.office365.com"
                    className="w-full px-3 py-2 text-[13px] bg-white border border-[#DCE3DE] rounded-md focus:outline-none focus:border-[#286B50]"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[12px] font-medium text-[#202824] mb-1">
                    Port Number
                  </label>
                  <input
                    type="number"
                    value={imapPort}
                    onChange={(e) => setImapPort(Number(e.target.value))}
                    className="w-full px-3 py-2 text-[13px] bg-white border border-[#DCE3DE] rounded-md focus:outline-none focus:border-[#286B50]"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[12px] font-medium text-[#202824] mb-1">
                    Email / Username
                  </label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="e.g. yourname@gmail.com"
                    className="w-full px-3 py-2 text-[13px] bg-white border border-[#DCE3DE] rounded-md focus:outline-none focus:border-[#286B50]"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[12px] font-medium text-[#202824] mb-1">
                    Password / App Password
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="App password (recommended) or mailbox password"
                    className="w-full px-3 py-2 text-[13px] bg-white border border-[#DCE3DE] rounded-md focus:outline-none focus:border-[#286B50]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[12px] font-medium text-[#202824] mb-1">
                    Target Mailbox / Folder
                  </label>
                  <input
                    type="text"
                    value={folder}
                    onChange={(e) => setFolder(e.target.value)}
                    className="w-full px-3 py-2 text-[13px] bg-white border border-[#DCE3DE] rounded-md focus:outline-none focus:border-[#286B50]"
                    required
                  />
                </div>
                <div className="flex items-center pt-6">
                  <label className="flex items-center gap-2 cursor-pointer text-[12px] text-[#202824] font-medium">
                    <input
                      type="checkbox"
                      checked={sslEnabled}
                      onChange={(e) => setSslEnabled(e.target.checked)}
                      className="rounded border-[#DCE3DE] text-[#286B50] focus:ring-[#286B50]"
                    />
                    <span>Enable TLS/SSL Encryption (Port 993)</span>
                  </label>
                </div>
              </div>

              <div className="pt-4 border-t border-[#DCE3DE] flex flex-wrap items-center justify-between gap-3">
                <button
                  type="button"
                  onClick={handleTestConnection}
                  disabled={testing}
                  className="px-3.5 py-2 text-[12px] font-medium text-[#202824] bg-white border border-[#DCE3DE] rounded-md hover:bg-[#F7F9F7] transition-colors disabled:opacity-50 flex items-center gap-1.5"
                >
                  {testing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Server className="w-3.5 h-3.5 text-[#286B50]" />}
                  <span>{testing ? 'Testing Handshake...' : 'Test IMAP Connection'}</span>
                </button>

                <div className="flex items-center gap-3">
                  {savedSuccess && (
                    <span className="text-[12px] text-[#16A34A] flex items-center gap-1 font-medium">
                      <Check className="w-3.5 h-3.5" /> Saved
                    </span>
                  )}
                  <button
                    type="submit"
                    disabled={syncing}
                    className="px-4 py-2 bg-[#286B50] hover:bg-[#1E5638] text-white text-[12px] font-semibold rounded-md transition-colors shadow-sm disabled:opacity-50 flex items-center gap-1.5"
                  >
                    {syncing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Mail className="w-3.5 h-3.5" />}
                    <span>{syncing ? 'Scanning Inbox...' : 'Save & Sync Real Mailbox'}</span>
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
