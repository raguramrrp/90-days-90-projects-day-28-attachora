import React from 'react';
import {
  Layers,
  Mail,
  ShieldCheck,
  Sliders,
  Folder,
  Clock,
  BarChart3,
  Settings,
} from 'lucide-react';

interface NavigationRailProps {
  activePage: string;
  onSelectPage: (page: string) => void;
}

export const NavigationRail: React.FC<NavigationRailProps> = ({
  activePage,
  onSelectPage,
}) => {
  const navItems = [
    { id: 'Queue', label: 'Attachment Queue', icon: Layers },
    { id: 'Mailbox', label: 'Email Connections & Ingestion', icon: Mail },
    { id: 'Integrity', label: 'Document & Storage Integrity', icon: ShieldCheck },
    { id: 'Rules', label: 'Smart Filing Rules', icon: Sliders },
    { id: 'Library', label: 'Organized Library Explorer', icon: Folder },
    { id: 'History', label: 'Operation History & Audit', icon: Clock },
    { id: 'Analytics', label: 'Operational Analytics', icon: BarChart3 },
  ];

  return (
    <aside className="w-[76px] flex-shrink-0 bg-white border-r border-[#DCE3DE] flex flex-col items-center py-4 justify-between h-screen select-none z-20">
      {/* Top Section with Logo & Nav items */}
      <div className="flex flex-col items-center w-full gap-2">
        {/* ATTACHORA Brand Logo Mark */}
        <div 
          onClick={() => onSelectPage('Queue')}
          className="w-10 h-10 bg-[#286B50] rounded-lg flex items-center justify-center cursor-pointer shadow-sm mb-4 hover:bg-[#20553F] transition-all"
          title="ATTACHORA Workstation"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="12 2 2 22 22 22 12 2"></polygon>
          </svg>
        </div>

        {/* Navigation Item Icons */}
        <div className="flex flex-col items-center w-full gap-1.5 px-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectPage(item.id)}
                title={item.label}
                className={`w-11 h-11 rounded-lg flex items-center justify-center transition-all duration-150 ${
                  isActive
                    ? 'bg-[#286B50] text-white shadow-sm'
                    : 'text-[#66716B] hover:bg-[#F1F6F2] hover:text-[#202824]'
                }`}
              >
                <Icon size={20} strokeWidth={2} />
              </button>
            );
          })}
        </div>
      </div>

      {/* Bottom Settings Button */}
      <div className="flex flex-col items-center w-full px-2">
        <button
          onClick={() => onSelectPage('Settings')}
          title="System Settings"
          className={`w-11 h-11 rounded-lg flex items-center justify-center transition-all duration-150 ${
            activePage === 'Settings'
              ? 'bg-[#286B50] text-white shadow-sm'
              : 'text-[#66716B] hover:bg-[#F1F6F2] hover:text-[#202824]'
          }`}
        >
          <Settings size={20} strokeWidth={2} />
        </button>
      </div>
    </aside>
  );
};
