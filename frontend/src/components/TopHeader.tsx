import React from 'react';
import { Download, ChevronDown } from 'lucide-react';

interface TopHeaderProps {
  activePage: string;
  onSelectPage: (page: string) => void;
  onImportClick: () => void;
  mailboxStatus?: string;
}

export const TopHeader: React.FC<TopHeaderProps> = ({
  activePage,
  onSelectPage,
  onImportClick,
  mailboxStatus = 'Local mailbox',
}) => {
  return (
    <header className="h-[58px] bg-white border-b border-[#DCE3DE] px-6 flex items-center justify-between select-none z-10 flex-shrink-0">
      {/* Left: Brand & Breadcrumb */}
      <div className="flex items-center gap-2.5">
        <span className="font-bold text-[15px] tracking-wide text-[#202824]">ATTACHORA</span>
        <span className="text-[#DCE3DE] font-light">|</span>
        <span className="text-[13px] text-[#66716B]">
          Workspace / <span className="font-medium text-[#202824]">{activePage === 'Queue' ? 'Attachment operations' : activePage}</span>
        </span>
      </div>

      {/* Right: Connection status & Action button */}
      <div className="flex items-center gap-3">
        <div 
          onClick={() => onSelectPage('Mailbox')}
          className="flex items-center gap-2 px-3 py-1.5 bg-white border border-[#DCE3DE] rounded-md text-[12px] font-medium text-[#202824] cursor-pointer hover:bg-[#F7F9F7] transition-all"
          title="Click to manage mailboxes"
        >
          <span className="w-2 h-2 rounded-full bg-[#278253]"></span>
          <span>{mailboxStatus}</span>
          <ChevronDown size={14} className="text-[#66716B]" />
        </div>

        <button
          onClick={onImportClick}
          className="flex items-center gap-1.5 px-3.5 py-1.5 bg-[#286B50] hover:bg-[#20553F] text-white rounded-md text-[13px] font-medium transition-all shadow-sm active:scale-98"
        >
          <Download size={15} strokeWidth={2.2} />
          <span>Import files</span>
        </button>
      </div>
    </header>
  );
};
