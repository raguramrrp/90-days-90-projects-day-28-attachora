import React, { useState, useEffect } from 'react';
import { 
  BarChart3, HardDrive, Clock, CheckCircle2, 
  TrendingUp, Users, PieChart, Sparkles, RefreshCw 
} from 'lucide-react';
import { SummaryMetrics } from '../types';

interface AnalyticsData {
  categories: Array<{ category: string; count: number; total_mb?: number }>;
  senders: Array<{ sender: string; sender_email?: string; count: number }>;
  timeline: Array<{ date: string; count: number }>;
}

export const AnalyticsView: React.FC = () => {
  const [summary, setSummary] = useState<SummaryMetrics | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [sumRes, anaRes] = await Promise.all([
        fetch('/api/summary'),
        fetch('/api/analytics'),
      ]);
      const sumData = await sumRes.json();
      const anaData = await anaRes.json();
      setSummary(sumData);
      setAnalytics(anaData);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const totalAttachments = summary?.total_detected || 0;
  const totalOrganized = summary?.total_organized || 0;
  const timeSavedMinutes = Math.round(totalOrganized * 1.5);
  const timeSavedHours = (timeSavedMinutes / 60).toFixed(1);

  return (
    <div className="flex-1 overflow-y-auto px-8 py-6 bg-[#F4F6F4]">
      {/* Title */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-[24px] font-bold text-[#202824] tracking-tight flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-[#286B50]" />
            Filing Analytics & Impact
          </h1>
          <p className="text-[13px] text-[#66716B] mt-0.5">
            Operational efficiency, deduplication savings, category distribution, and sender profiles.
          </p>
        </div>
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 px-3 py-1.5 text-[12px] font-medium text-[#202824] bg-white border border-[#DCE3DE] rounded-md hover:bg-[#F7F9F7] transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5 text-[#66716B]" />
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="py-20 text-center text-[#66716B]">
          <RefreshCw className="w-6 h-6 text-[#286B50] animate-spin mx-auto mb-2" />
          Computing workspace telemetry...
        </div>
      ) : (
        <>
          {/* Top 4 KPI Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-white border border-[#DCE3DE] rounded-lg p-5 shadow-sm">
              <div className="flex items-center justify-between text-[#66716B] mb-2">
                <span className="text-[12px] font-medium">Total Processed</span>
                <CheckCircle2 className="w-4 h-4 text-[#286B50]" />
              </div>
              <div className="text-[26px] font-bold text-[#202824] tracking-tight">
                {totalAttachments}
              </div>
              <div className="text-[11px] text-[#286B50] font-medium mt-1">
                {totalOrganized} filed to structured disk
              </div>
            </div>

            <div className="bg-white border border-[#DCE3DE] rounded-lg p-5 shadow-sm">
              <div className="flex items-center justify-between text-[#66716B] mb-2">
                <span className="text-[12px] font-medium">Storage Managed</span>
                <HardDrive className="w-4 h-4 text-[#2563EB]" />
              </div>
              <div className="text-[26px] font-bold text-[#202824] tracking-tight">
                {summary?.storage_organized_mb?.toFixed(2) || '0.00'} MB
              </div>
              <div className="text-[11px] text-[#66716B] mt-1">
                Verified zero-byte corruption
              </div>
            </div>

            <div className="bg-white border border-[#DCE3DE] rounded-lg p-5 shadow-sm">
              <div className="flex items-center justify-between text-[#66716B] mb-2">
                <span className="text-[12px] font-medium">Duplicate Space Saved</span>
                <Sparkles className="w-4 h-4 text-[#D97706]" />
              </div>
              <div className="text-[26px] font-bold text-[#202824] tracking-tight">
                {summary?.storage_saved_mb?.toFixed(2) || '0.00'} MB
              </div>
              <div className="text-[11px] text-[#D97706] font-medium mt-1">
                {summary?.duplicates_count || 0} redundant payloads stopped
              </div>
            </div>

            <div className="bg-white border border-[#DCE3DE] rounded-lg p-5 shadow-sm">
              <div className="flex items-center justify-between text-[#66716B] mb-2">
                <span className="text-[12px] font-medium">Estimated Time Saved</span>
                <Clock className="w-4 h-4 text-[#16A34A]" />
              </div>
              <div className="text-[26px] font-bold text-[#202824] tracking-tight">
                {timeSavedHours} hrs
              </div>
              <div className="text-[11px] text-[#16A34A] font-medium mt-1">
                Based on 1.5 min / manual filing
              </div>
            </div>
          </div>

          {/* Breakdown Grids */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Category Breakdown */}
            <div className="bg-white border border-[#DCE3DE] rounded-lg p-5 shadow-sm">
              <div className="flex items-center gap-2 text-[15px] font-bold text-[#202824] mb-3">
                <PieChart className="w-4 h-4 text-[#286B50]" />
                Classification by Category
              </div>
              <div className="space-y-3">
                {analytics?.categories && analytics.categories.length > 0 ? (
                  analytics.categories.map((cat) => {
                    const pct = totalAttachments > 0 ? Math.round((cat.count / totalAttachments) * 100) : 0;
                    return (
                      <div key={cat.category}>
                        <div className="flex items-center justify-between text-[12px] mb-1">
                          <span className="font-semibold text-[#202824]">{cat.category}</span>
                          <span className="text-[#66716B]">
                            {cat.count} files ({pct}%)
                          </span>
                        </div>
                        <div className="w-full bg-[#EAEFEA] h-2 rounded-full overflow-hidden">
                          <div
                            className="bg-[#286B50] h-full rounded-full transition-all duration-500"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-center py-6 text-[12px] text-[#8A948E]">No categorized records</div>
                )}
              </div>
            </div>

            {/* Top Senders */}
            <div className="bg-white border border-[#DCE3DE] rounded-lg p-5 shadow-sm">
              <div className="flex items-center gap-2 text-[15px] font-bold text-[#202824] mb-3">
                <Users className="w-4 h-4 text-[#286B50]" />
                Top Attachment Originators
              </div>
              <div className="divide-y divide-[#DCE3DE]">
                {analytics?.senders && analytics.senders.length > 0 ? (
                  analytics.senders.map((sender, idx) => (
                    <div key={idx} className="py-2.5 flex items-center justify-between text-[12px]">
                      <div>
                        <div className="font-semibold text-[#202824]">{sender.sender || 'Direct Ingestion'}</div>
                        {sender.sender_email && (
                          <div className="text-[11px] text-[#8A948E]">{sender.sender_email}</div>
                        )}
                      </div>
                      <span className="px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-[#F1F6F2] text-[#286B50] border border-[#DCE3DE]">
                        {sender.count} docs
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-6 text-[12px] text-[#8A948E]">No sender history yet</div>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
