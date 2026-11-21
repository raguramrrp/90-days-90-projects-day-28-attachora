import React, { useState } from 'react';
import { 
  ShieldCheck, AlertTriangle, FileCode, CheckCircle2, 
  Terminal, ShieldAlert, Lock, ArrowRight, RefreshCw 
} from 'lucide-react';

export const IntegrityView: React.FC = () => {
  // Path Sanitizer Live Sandbox
  const [inputFilename, setInputFilename] = useState<string>('CON.txt');
  const [sanitizedResult, setSanitizedResult] = useState<string>('con_safe.txt');

  // Interactive SHA-256 calculator test
  const [inputString, setInputString] = useState<string>('Attachora Secure Document Verification 2026');
  const [hashResult, setHashResult] = useState<string>('');

  const sanitizeClientSide = (input: string): string => {
    let name = input.replace(/[/\\?%*:|"<>]/g, '_');
    const reserved = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'];
    const parts = name.split('.');
    const base = parts[0].toUpperCase();
    if (reserved.includes(base)) {
      parts[0] = `${parts[0]}_safe`;
      name = parts.join('.');
    }
    return name.trim() || 'unnamed_attachment';
  };

  const handleFilenameChange = (val: string) => {
    setInputFilename(val);
    setSanitizedResult(sanitizeClientSide(val));
  };

  const calculateHash = async () => {
    const encoder = new TextEncoder();
    const data = encoder.encode(inputString);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    setHashResult(hashHex);
  };

  return (
    <div className="flex-1 overflow-y-auto px-8 py-6 bg-[#F4F6F4]">
      {/* Title */}
      <div className="mb-6">
        <h1 className="text-[24px] font-bold text-[#202824] tracking-tight flex items-center gap-2">
          <ShieldCheck className="w-6 h-6 text-[#286B50]" />
          Integrity & Security Center
        </h1>
        <p className="text-[13px] text-[#66716B] mt-0.5">
          Cryptographic hash audits, archive bomb defense heuristics, and path-traversal sanitization tools.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Path Traversal & Windows Device Name Sanitizer */}
        <div className="bg-white border border-[#DCE3DE] rounded-lg p-5 shadow-sm">
          <div className="flex items-center gap-2 text-[15px] font-bold text-[#202824] mb-1">
            <Terminal className="w-4 h-4 text-[#286B50]" />
            Filename Sanitizer Sandbox
          </div>
          <p className="text-[12px] text-[#66716B] mb-4">
            Test how ATTACHORA neutralizes Windows reserved device names (CON, PRN, AUX, NUL), ADS alternate data streams, and <code>../</code> traversal attempts.
          </p>

          <div className="space-y-3">
            <div>
              <label className="block text-[11px] font-medium text-[#66716B] mb-1">
                Raw Input Filename:
              </label>
              <input
                type="text"
                value={inputFilename}
                onChange={(e) => handleFilenameChange(e.target.value)}
                className="w-full px-3 py-2 text-[13px] font-mono bg-[#F7F9F7] border border-[#DCE3DE] rounded-md focus:outline-none focus:border-[#286B50]"
                placeholder="e.g. CON.txt or ../../etc/passwd"
              />
            </div>

            <div className="flex items-center justify-center py-1">
              <ArrowRight className="w-4 h-4 text-[#8A948E]" />
            </div>

            <div>
              <label className="block text-[11px] font-medium text-[#66716B] mb-1">
                Sanitized Safe Disk Filename:
              </label>
              <div className="w-full px-3 py-2 text-[13px] font-mono bg-[#EBF7F0] border border-[#A3D9B8] text-[#1E5638] rounded-md font-semibold">
                {sanitizedResult}
              </div>
            </div>

            <div className="pt-3 border-t border-[#DCE3DE]">
              <span className="text-[11px] font-medium text-[#66716B] block mb-1.5">Try sample attacks:</span>
              <div className="flex flex-wrap gap-1.5">
                {['CON.txt', 'PRN', '../../secret.docx', 'invoice:hidden_stream.pdf', 'aux.png'].map((sample) => (
                  <button
                    key={sample}
                    onClick={() => handleFilenameChange(sample)}
                    className="px-2 py-0.5 text-[11px] font-mono bg-[#F4F6F4] hover:bg-[#EAEFEA] text-[#286B50] rounded border border-[#DCE3DE]"
                  >
                    {sample}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* SHA-256 Hash Verifier */}
        <div className="bg-white border border-[#DCE3DE] rounded-lg p-5 shadow-sm">
          <div className="flex items-center gap-2 text-[15px] font-bold text-[#202824] mb-1">
            <Lock className="w-4 h-4 text-[#286B50]" />
            SHA-256 Digest Calculator
          </div>
          <p className="text-[12px] text-[#66716B] mb-4">
            Demonstrates real-time 256-bit cryptographic fingerprinting used across the deduplication pipeline.
          </p>

          <div className="space-y-3">
            <div>
              <label className="block text-[11px] font-medium text-[#66716B] mb-1">
                Input Text Payload:
              </label>
              <textarea
                value={inputString}
                onChange={(e) => setInputString(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 text-[12px] font-mono bg-[#F7F9F7] border border-[#DCE3DE] rounded-md focus:outline-none focus:border-[#286B50]"
              />
            </div>

            <button
              onClick={calculateHash}
              className="px-3.5 py-1.5 text-[12px] font-semibold text-white bg-[#286B50] hover:bg-[#1E5638] rounded-md transition-colors"
            >
              Compute SHA-256 Hash
            </button>

            {hashResult && (
              <div>
                <label className="block text-[11px] font-medium text-[#66716B] mb-1">
                  Hex Digest (64 characters):
                </label>
                <div className="p-2.5 bg-[#F1F6F2] border border-[#DCE3DE] rounded-md font-mono text-[11px] text-[#286B50] break-all select-all">
                  {hashResult}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Archive Bomb Defense Specifications */}
        <div className="lg:col-span-2 bg-white border border-[#DCE3DE] rounded-lg p-5 shadow-sm">
          <div className="flex items-center gap-2 text-[15px] font-bold text-[#202824] mb-1">
            <ShieldAlert className="w-4 h-4 text-[#D97706]" />
            Active Archive Bomb Defense Safeguards
          </div>
          <p className="text-[12px] text-[#66716B] mb-4">
            Parameters enforced before unpacking or processing compressed archives (.zip, .tar, .gz):
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-lg bg-[#F7F9F7] border border-[#DCE3DE]">
              <div className="text-[12px] text-[#66716B] font-medium">Max Compression Ratio</div>
              <div className="text-[20px] font-bold text-[#202824] mt-1">100 : 1</div>
              <p className="text-[11px] text-[#8A948E] mt-1">
                Archives with ratio exceeding 100x are flagged as decompression bombs and quarantined.
              </p>
            </div>

            <div className="p-4 rounded-lg bg-[#F7F9F7] border border-[#DCE3DE]">
              <div className="text-[12px] text-[#66716B] font-medium">Max Uncompressed Size</div>
              <div className="text-[20px] font-bold text-[#202824] mt-1">50.0 MB</div>
              <p className="text-[11px] text-[#8A948E] mt-1">
                Stops memory exhaustion attacks attempting to unpack gigabyte payloads into memory.
              </p>
            </div>

            <div className="p-4 rounded-lg bg-[#F7F9F7] border border-[#DCE3DE]">
              <div className="text-[12px] text-[#66716B] font-medium">Nested Archive Limit</div>
              <div className="text-[20px] font-bold text-[#202824] mt-1">3 Layers</div>
              <p className="text-[11px] text-[#8A948E] mt-1">
                Recursion depth capped at 3 levels to neutralize recursive zip-within-zip loops.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
