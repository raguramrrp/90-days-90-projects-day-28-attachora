import React, { useState } from 'react';
import { 
  Settings, Folder, Sliders, Shield, Database, 
  Check, HardDrive, AlertCircle, Save 
} from 'lucide-react';

export const SettingsView: React.FC = () => {
  const [baseFolder, setBaseFolder] = useState<string>('organized');
  const [duplicatePolicy, setDuplicatePolicy] = useState<string>('keep_copy');
  const [confidenceThreshold, setConfidenceThreshold] = useState<number>(85);
  const [autoOrganize, setAutoOrganize] = useState<boolean>(false);
  const [namingTemplate, setNamingTemplate] = useState<string>('{date}_{category}_{original_filename}');
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="flex-1 overflow-y-auto px-8 py-6 bg-[#F4F6F4]">
      {/* Title */}
      <div className="mb-6">
        <h1 className="text-[24px] font-bold text-[#202824] tracking-tight flex items-center gap-2">
          <Settings className="w-6 h-6 text-[#286B50]" />
          System Preferences & Filing Engine
        </h1>
        <p className="text-[13px] text-[#66716B] mt-0.5">
          Filing destinations, deduplication policies, filename standardization, and machine storage configurations.
        </p>
      </div>

      <div className="max-w-4xl space-y-6">
        <form onSubmit={handleSave} className="space-y-6">
          {/* Storage & Filing Destination */}
          <div className="bg-white border border-[#DCE3DE] rounded-lg p-6 shadow-sm">
            <h2 className="text-[15px] font-bold text-[#202824] mb-1 flex items-center gap-2">
              <Folder className="w-4 h-4 text-[#286B50]" />
              Filing Storage Directory
            </h2>
            <p className="text-[12px] text-[#66716B] mb-4">
              All approved documents and attachments will be written into categorized subfolders under this base directory.
            </p>

            <div className="space-y-3">
              <div>
                <label className="block text-[12px] font-medium text-[#202824] mb-1">
                  Root Destination Path
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={baseFolder}
                    onChange={(e) => setBaseFolder(e.target.value)}
                    className="flex-1 px-3 py-2 text-[13px] font-mono bg-white border border-[#DCE3DE] rounded-md focus:outline-none focus:border-[#286B50]"
                  />
                  <span className="text-[11px] text-[#8A948E] font-mono">/ (workspace relative)</span>
                </div>
              </div>

              <div>
                <label className="block text-[12px] font-medium text-[#202824] mb-1">
                  Standard Filename Template
                </label>
                <input
                  type="text"
                  value={namingTemplate}
                  onChange={(e) => setNamingTemplate(e.target.value)}
                  className="w-full px-3 py-2 text-[13px] font-mono bg-white border border-[#DCE3DE] rounded-md focus:outline-none focus:border-[#286B50]"
                />
                <span className="text-[11px] text-[#8A948E] mt-1 block">
                  Available tags: <code>{'{date}'}</code>, <code>{'{category}'}</code>, <code>{'{original_filename}'}</code>, <code>{'{sender}'}</code>
                </span>
              </div>
            </div>
          </div>

          {/* Deduplication Strategy */}
          <div className="bg-white border border-[#DCE3DE] rounded-lg p-6 shadow-sm">
            <h2 className="text-[15px] font-bold text-[#202824] mb-1 flex items-center gap-2">
              <Shield className="w-4 h-4 text-[#286B50]" />
              Collision & Duplicate Strategy
            </h2>
            <p className="text-[12px] text-[#66716B] mb-4">
              How the system acts when an attachment matches an existing SHA-256 hash or destination filename.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {[
                { id: 'keep_copy', label: 'Version Increment', desc: 'Saves duplicate with (_1, _2) suffix to preserve version history.' },
                { id: 'skip', label: 'Skip Duplicate', desc: 'Bypasses writing duplicate payloads to disk to conserve storage.' },
                { id: 'quarantine', label: 'Quarantine', desc: 'Moves into isolated quarantine directory for manual operator review.' },
              ].map((opt) => (
                <label
                  key={opt.id}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    duplicatePolicy === opt.id
                      ? 'border-[#286B50] bg-[#F1F6F2]'
                      : 'border-[#DCE3DE] bg-white hover:bg-[#F7F9F7]'
                  }`}
                >
                  <input
                    type="radio"
                    name="dup_policy"
                    value={opt.id}
                    checked={duplicatePolicy === opt.id}
                    onChange={(e) => setDuplicatePolicy(e.target.value)}
                    className="sr-only"
                  />
                  <div className="text-[13px] font-bold text-[#202824]">{opt.label}</div>
                  <div className="text-[11px] text-[#66716B] mt-1">{opt.desc}</div>
                </label>
              ))}
            </div>
          </div>

          {/* Confidence & Automation */}
          <div className="bg-white border border-[#DCE3DE] rounded-lg p-6 shadow-sm">
            <h2 className="text-[15px] font-bold text-[#202824] mb-1 flex items-center gap-2">
              <Sliders className="w-4 h-4 text-[#286B50]" />
              Automation Confidence Bar
            </h2>
            <p className="text-[12px] text-[#66716B] mb-4">
              Attachments with classification confidence at or above this threshold will be marked "Ready to File".
            </p>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-[12px] font-medium text-[#202824] mb-1">
                  <span>Minimum Required Confidence</span>
                  <span className="font-mono text-[#286B50] font-bold">{confidenceThreshold}%</span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="98"
                  value={confidenceThreshold}
                  onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
                  className="w-full accent-[#286B50] cursor-pointer"
                />
              </div>

              <div className="flex items-center gap-2 pt-2 border-t border-[#DCE3DE]">
                <input
                  type="checkbox"
                  id="auto_file"
                  checked={autoOrganize}
                  onChange={(e) => setAutoOrganize(e.target.checked)}
                  className="rounded border-[#DCE3DE] text-[#286B50] focus:ring-[#286B50]"
                />
                <label htmlFor="auto_file" className="text-[12px] text-[#202824] font-medium cursor-pointer">
                  Auto-file documents with 95%+ confidence without operator confirmation
                </label>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex items-center justify-between pt-2">
            <div className="text-[12px] text-[#66716B]">
              {savedSuccess ? (
                <span className="text-[#16A34A] font-semibold flex items-center gap-1">
                  <Check className="w-4 h-4" /> Preferences updated successfully
                </span>
              ) : (
                'Settings take effect on the next incoming scan.'
              )}
            </div>
            <button
              type="submit"
              className="flex items-center gap-2 px-5 py-2.5 bg-[#286B50] hover:bg-[#1E5638] text-white text-[13px] font-semibold rounded-md shadow-sm transition-colors"
            >
              <Save className="w-4 h-4" />
              Save Preferences
            </button>
          </div>
        </form>

        {/* Database Stats Card */}
        <div className="bg-white border border-[#DCE3DE] rounded-lg p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-[14px] font-bold text-[#202824]">
              <Database className="w-4 h-4 text-[#286B50]" />
              Persistent Metadata Storage (SQLite)
            </div>
            <span className="text-[11px] font-mono text-[#286B50] bg-[#EBF7F0] px-2 py-0.5 rounded border border-[#A3D9B8]">
              attachora.db · Operational
            </span>
          </div>
          <div className="mt-2 text-[12px] text-[#66716B]">
            All rules, duplicate hash indices, metadata, and immutable operation history are stored with WAL mode enabled.
          </div>
        </div>
      </div>
    </div>
  );
};
