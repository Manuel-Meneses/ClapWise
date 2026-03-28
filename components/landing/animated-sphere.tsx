"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { Layers, Workflow, Database, Cpu, SearchCode, LineChart } from "lucide-react";

// Representamos el ecosistema completo de ClapWise
const solutions = [
  { id: "saas", icon: Layers, label: "Desarrollo SaaS IA", detail: "Software escalable", color: "text-[var(--primary)]" },
  { id: "rpa", icon: Workflow, label: "Automatización RPA", detail: "Cero tareas manuales", color: "text-[var(--secondary)]" },
  { id: "data", icon: LineChart, label: "Data Intelligence", detail: "Decisiones con datos", color: "text-green-500" },
  { id: "infra", icon: Cpu, label: "Infraestructura IA", detail: "Sistemas autónomos", color: "text-orange-500" },
];

export function AnimatedSphere() {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setActive((prev) => (prev + 1) % solutions.length), 3500);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="w-full max-w-[550px] bg-white/40 backdrop-blur-2xl rounded-[2.5rem] border border-[var(--border)] shadow-2xl overflow-hidden flex flex-col transition-all duration-500 hover:shadow-[var(--primary)]/5 group">
      {/* Barra de título estilo Mac/Software Premium */}
      <div className="px-8 py-5 border-b border-[var(--border)] bg-white/50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-[var(--primary)]/40" />
            <div className="w-3 h-3 rounded-full bg-[var(--primary)]/20" />
          </div>
          <span className="text-[10px] font-mono tracking-widest text-[var(--muted-foreground)] uppercase">ClapWise Solutions Lab</span>
        </div>
        <div className="px-3 py-1 rounded-full bg-[var(--muted)] border border-[var(--primary)]/10">
          <span className="text-[9px] font-bold text-[var(--primary)] animate-pulse">SYSTEM_ONLINE</span>
        </div>
      </div>

      <div className="flex-1 p-8 lg:p-10 flex flex-col gap-8">
        {/* Pantalla de visualización principal */}
        <div className="h-48 rounded-2xl bg-[var(--foreground)] p-6 relative overflow-hidden flex items-center justify-center">
          <div className="absolute inset-0 opacity-20" style={{ backgroundImage: `radial-gradient(circle at 2px 2px, var(--muted) 1px, transparent 0)`, backgroundSize: '24px 24px' }} />
          
          <div className="relative z-10 flex flex-col items-center text-center">
            <div className={cn("mb-4 transition-all duration-700 transform", solutions[active].color)}>
              {(() => {
                const Icon = solutions[active].icon;
                return <Icon size={48} strokeWidth={1.5} className="drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]" />;
              })()}
            </div>
            <h4 className="text-white font-display text-xl tracking-wide">{solutions[active].label}</h4>
            <p className="text-white/50 text-xs font-mono mt-1">{solutions[active].detail}</p>
          </div>
        </div>

        {/* Selector de módulos (Grid de soluciones) */}
        <div className="grid grid-cols-2 gap-4">
          {solutions.map((item, idx) => {
            const Icon = item.icon;
            const isActive = idx === active;
            return (
              <div
                key={item.id}
                className={cn(
                  "p-4 rounded-2xl border transition-all duration-500 flex items-center gap-4",
                  isActive 
                    ? "bg-white border-[var(--primary)]/20 shadow-lg scale-[1.02]" 
                    : "bg-transparent border-transparent opacity-40 grayscale"
                )}
              >
                <div className={cn("w-10 h-10 rounded-xl bg-[var(--muted)] flex items-center justify-center shrink-0", isActive && item.color)}>
                  <Icon size={20} />
                </div>
                <div className="flex flex-col overflow-hidden">
                  <span className="text-[11px] font-bold text-[var(--foreground)] truncate">{item.label}</span>
                  <span className="text-[9px] text-[var(--muted-foreground)] uppercase tracking-tighter">Módulo Activo</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}