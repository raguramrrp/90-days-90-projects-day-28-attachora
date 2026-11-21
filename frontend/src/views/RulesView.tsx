import React, { useState, useEffect } from 'react';
import { Sliders, Plus, Trash2, CheckCircle2 } from 'lucide-react';
import { FilingRule } from '../types';

export const RulesView: React.FC = () => {
  const [rules, setRules] = useState<FilingRule[]>([]);
  const [loading, setLoading] = useState(true);

  // New rule form
  const [ruleName, setRuleName] = useState('');
  const [destination, setDestination] = useState('');
  const [priority, setPriority] = useState(10);
  const [field, setField] = useState('category');
  const [operator, setOperator] = useState('equals');
  const [condValue, setCondValue] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const fetchRules = async () => {
    try {
      const res = await fetch('/api/rules');
      const data = await res.json();
      setRules(data.rules || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ruleName || !destination || !condValue) return;

    try {
      const res = await fetch('/api/rules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rule_name: ruleName,
          destination,
          priority,
          filename_template: '{date}_{category}_{original_filename}',
          conditions: {
            logic: 'AND',
            rules: [{ field, operator, value: condValue }],
          },
        }),
      });
      const data = await res.json();
      if (data.success) {
        setSuccessMsg(`Rule '${ruleName}' created successfully.`);
        setRuleName('');
        setDestination('');
        setCondValue('');
        fetchRules();
        setTimeout(() => setSuccessMsg(''), 4000);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteRule = async (id: number) => {
    try {
      await fetch(`/api/rules/${id}`, { method: 'DELETE' });
      fetchRules();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex-1 p-6 overflow-y-auto space-y-5">
      <div>
        <h1 className="text-[22px] font-bold text-[#202824]">Smart Filing Rules</h1>
        <p className="text-[13px] text-[#66716B]">Define prioritized routing rules and directory mapping templates.</p>
      </div>

      {successMsg && (
        <div className="bg-[#E9F2EC] border border-[#C9E2D2] text-[#278253] text-[13px] px-4 py-2.5 rounded-md flex items-center gap-2">
          <CheckCircle2 size={16} />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Rules Table */}
      <div className="bg-white border border-[#DCE3DE] rounded-lg overflow-hidden shadow-sm">
        <div className="bg-[#F7F9F7] px-4 py-2.5 border-b border-[#DCE3DE] text-[11px] font-bold text-[#66716B] uppercase tracking-wider">
          Configured Priority Rules
        </div>
        <table className="w-full text-left text-[13px]">
          <thead>
            <tr className="border-b border-[#DCE3DE] text-[11px] font-semibold text-[#66716B]">
              <th className="py-2.5 px-4 w-16">RANK</th>
              <th className="py-2.5 px-4">RULE NAME</th>
              <th className="py-2.5 px-4">DESTINATION DIRECTORY</th>
              <th className="py-2.5 px-4">CONDITIONS</th>
              <th className="py-2.5 px-4 text-center w-24">STATUS</th>
              <th className="py-2.5 px-4 text-right w-20">ACTION</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#EAEFEA]">
            {rules.map((rule) => (
              <tr key={rule.id} className="hover:bg-[#F1F6F2] transition-colors">
                <td className="py-2.5 px-4 font-mono font-bold text-[#286B50]">#{rule.priority}</td>
                <td className="py-2.5 px-4 font-medium text-[#202824]">{rule.rule_name}</td>
                <td className="py-2.5 px-4 font-mono text-[12px] text-[#66716B]">/{rule.destination}</td>
                <td className="py-2.5 px-4 text-[11px] text-[#66716B] font-mono truncate max-w-[260px]">{rule.conditions_json}</td>
                <td className="py-2.5 px-4 text-center">
                  <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-[#E9F2EC] text-[#278253]">Active</span>
                </td>
                <td className="py-2.5 px-4 text-right">
                  <button
                    onClick={() => handleDeleteRule(rule.id)}
                    className="text-[#BD4545] hover:text-red-700 p-1"
                    title="Delete rule"
                  >
                    <Trash2 size={15} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Create New Rule Form */}
      <div className="bg-white border border-[#DCE3DE] rounded-lg p-5 shadow-sm">
        <h2 className="text-[14px] font-bold text-[#202824] mb-3 flex items-center gap-2">
          <Plus size={16} className="text-[#286B50]" />
          <span>Create New Filing Rule</span>
        </h2>
        <form onSubmit={handleCreateRule} className="grid grid-cols-3 gap-4 text-[13px]">
          <div>
            <label className="block text-[11px] font-semibold text-[#66716B] mb-1">Rule Name</label>
            <input
              type="text"
              value={ruleName}
              onChange={(e) => setRuleName(e.target.value)}
              placeholder="e.g. Stripe Receipts to Invoices"
              className="w-full bg-white border border-[#DCE3DE] rounded px-3 py-1.5 text-[#202824] focus:outline-none focus:border-[#286B50]"
              required
            />
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-[#66716B] mb-1">Destination Subfolder</label>
            <input
              type="text"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              placeholder="e.g. Finance/Invoices"
              className="w-full bg-white border border-[#DCE3DE] rounded px-3 py-1.5 text-[#202824] focus:outline-none focus:border-[#286B50]"
              required
            />
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-[#66716B] mb-1">Priority Rank (1 = Highest)</label>
            <input
              type="number"
              value={priority}
              onChange={(e) => setPriority(parseInt(e.target.value) || 10)}
              className="w-full bg-white border border-[#DCE3DE] rounded px-3 py-1.5 text-[#202824] focus:outline-none focus:border-[#286B50]"
              min={1}
              max={99}
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-[#66716B] mb-1">Condition Field</label>
            <select
              value={field}
              onChange={(e) => setField(e.target.value)}
              className="w-full bg-white border border-[#DCE3DE] rounded px-3 py-1.5 text-[#202824] focus:outline-none focus:border-[#286B50]"
            >
              <option value="category">Category</option>
              <option value="filename">Filename</option>
              <option value="sender_email">Sender Email</option>
              <option value="subject">Subject</option>
              <option value="extension">Extension</option>
            </select>
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-[#66716B] mb-1">Operator</label>
            <select
              value={operator}
              onChange={(e) => setOperator(e.target.value)}
              className="w-full bg-white border border-[#DCE3DE] rounded px-3 py-1.5 text-[#202824] focus:outline-none focus:border-[#286B50]"
            >
              <option value="equals">Equals</option>
              <option value="contains">Contains</option>
              <option value="starts_with">Starts With</option>
              <option value="ends_with">Ends With</option>
            </select>
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-[#66716B] mb-1">Matching Value</label>
            <input
              type="text"
              value={condValue}
              onChange={(e) => setCondValue(e.target.value)}
              placeholder="e.g. Invoices or stripe.com"
              className="w-full bg-white border border-[#DCE3DE] rounded px-3 py-1.5 text-[#202824] focus:outline-none focus:border-[#286B50]"
              required
            />
          </div>

          <div className="col-span-3 flex justify-end pt-2">
            <button
              type="submit"
              className="px-4 py-2 bg-[#286B50] hover:bg-[#20553F] text-white rounded font-medium shadow-sm"
            >
              Save New Filing Rule
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
