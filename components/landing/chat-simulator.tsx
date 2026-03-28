"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

const messages = [
  { text: "¡Hola! Necesito un presupuesto para instalar un aire acondicionado. ¿Tienen disponibilidad?", sender: "client", time: "02:14 AM" },
  { text: "¡Hola! Soy el asistente virtual de la empresa ⚡. Claro que sí. Para darte un precio exacto, ¿de cuántas frigorías es el equipo?", sender: "bot", time: "02:14 AM" },
  { text: "Es de 3000 frigorías. Lo compré hoy.", sender: "client", time: "02:15 AM" },
  { text: "Perfecto. La instalación base es de $50 USD. Tenemos un turno libre mañana a las 14:30 hs. ¿Te lo reservo?", sender: "bot", time: "02:15 AM" },
  { text: "Sí, por favor. Mi nombre es Carlos.", sender: "client", time: "02:16 AM" },
  { text: "¡Listo Carlos! Turno agendado en nuestro sistema. El técnico te visitará mañana. 🛠️", sender: "bot", time: "02:16 AM" },
];

export function ChatSimulator() {
  const [visibleMessages, setVisibleMessages] = useState<number>(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setVisibleMessages((prev) => (prev < messages.length ? prev + 1 : prev));
    }, 2500); // Aparece un mensaje cada 2.5 segundos

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="relative w-[320px] h-[600px] bg-white rounded-[2.5rem] border-8 border-[var(--foreground)] shadow-2xl overflow-hidden flex flex-col mx-auto">
      {/* Header estilo WhatsApp */}
      <div className="bg-[var(--primary)] text-white px-4 py-3 flex items-center gap-3 shadow-md z-10">
        <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center shrink-0">
          <span className="font-bold text-sm">IA</span>
        </div>
        <div className="flex flex-col">
          <span className="font-semibold text-sm">Asistente ClapWise</span>
          <span className="text-[10px] text-white/80">en línea</span>
        </div>
      </div>

      {/* Fondo de chat (Pale Sky muy suave) */}
      <div className="flex-1 bg-[var(--muted)]/30 p-4 overflow-y-auto flex flex-col gap-3">
        {messages.slice(0, visibleMessages).map((msg, idx) => (
          <div
            key={idx}
            className={cn(
              "max-w-[85%] rounded-2xl px-4 py-2 text-sm shadow-sm animate-in fade-in slide-in-from-bottom-2",
              msg.sender === "bot"
                ? "bg-[var(--primary)] text-white self-start rounded-tl-sm"
                : "bg-white text-[var(--foreground)] self-end rounded-tr-sm"
            )}
          >
            <p className="leading-relaxed">{msg.text}</p>
            <span className={cn(
              "text-[9px] block mt-1 text-right",
              msg.sender === "bot" ? "text-white/70" : "text-[var(--muted-foreground)]"
            )}>
              {msg.time}
            </span>
          </div>
        ))}

        {/* Indicador de "Escribiendo..." */}
        {visibleMessages > 0 && visibleMessages < messages.length && visibleMessages % 2 !== 0 && (
          <div className="bg-[var(--primary)] text-white self-start rounded-2xl rounded-tl-sm px-4 py-2 text-sm shadow-sm animate-pulse flex gap-1 items-center">
            <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" />
            <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce delay-75" />
            <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce delay-150" />
          </div>
        )}
      </div>

      {/* Input de abajo */}
      <div className="bg-white p-3 flex gap-2 items-center border-t border-[var(--border)]">
        <div className="flex-1 bg-[var(--muted)]/50 rounded-full h-10 px-4 flex items-center text-sm text-[var(--muted-foreground)]">
          Mensaje...
        </div>
        <div className="w-10 h-10 rounded-full bg-[var(--primary)] flex items-center justify-center shrink-0">
          <div className="w-0 h-0 border-t-[6px] border-t-transparent border-l-[10px] border-l-white border-b-[6px] border-b-transparent ml-1" />
        </div>
      </div>
    </div>
  );
}