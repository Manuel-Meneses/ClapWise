"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { AnimatedSphere } from "./animated-sphere";
import { ChatSimulator } from "./chat-simulator";

const words = ["Filtra", "Atiende", "Agenda", "Vende"];

export function HeroSection() {
  const [isVisible, setIsVisible] = useState(false);
  const [wordIndex, setWordIndex] = useState(0);

  useEffect(() => { setIsVisible(true); }, []);
  useEffect(() => {
    const interval = setInterval(() => setWordIndex((prev) => (prev + 1) % words.length), 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative min-h-screen flex flex-col justify-center overflow-hidden bg-background">
     <div className="hidden lg:flex items-center justify-center w-[500px] h-[600px]">
   <ChatSimulator />
    </div> 
      
      <div className="relative z-10 max-w-[1400px] mx-auto px-6 lg:px-12 py-32 lg:py-40">
        <div className={`mb-8 transition-all duration-700 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
          <span className="inline-flex items-center gap-3 text-sm font-mono text-primary font-semibold uppercase tracking-wider">
            <span className="w-8 h-px bg-primary" />
            La evolución de la atención al cliente
          </span>
        </div>
        
        <div className="mb-12">
          <h1 className={`text-[clamp(3rem,10vw,8rem)] font-display leading-[0.9] tracking-tight text-foreground transition-all duration-1000 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}>
            <span className="block">El asistente que</span>
            <span className="block">
              <span className="relative inline-block text-primary">
                <span key={wordIndex} className="inline-flex">
                  {words[wordIndex].split("").map((char, i) => (
                    <span key={`${wordIndex}-${i}`} className="inline-block animate-char-in" style={{ animationDelay: `${i * 50}ms` }}>
                      {char}
                    </span>
                  ))}
                </span>
                <span className="absolute -bottom-2 left-0 right-0 h-3 bg-secondary/30" />
              </span>
              {" "}por tu negocio.
            </span>
          </h1>
        </div>
        
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-24 items-end">
          <p className={`text-xl lg:text-2xl text-muted-foreground leading-relaxed max-w-xl transition-all duration-700 delay-200 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            Sistemas de IA integrados a tu WhatsApp que califican clientes y agendan turnos automáticamente. <strong>Deja de perder dinero fuera del horario comercial.</strong>
          </p>
          
          <div className={`flex flex-col sm:flex-row items-start gap-4 transition-all duration-700 delay-300 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            <Button size="lg" className="bg-primary hover:bg-primary/90 text-white px-8 h-14 text-base rounded-full shadow-lg shadow-primary/25 group">
              Solicitar Demostración
              <ArrowRight className="w-4 h-4 ml-2 transition-transform group-hover:translate-x-1" />
            </Button>
          </div>
        </div>
      </div>
      
      {/* Métricas de negocio */}
      <div className={`absolute bottom-0 left-0 right-0 bg-muted transition-all duration-700 delay-500 ${isVisible ? "opacity-100" : "opacity-0"}`}>
        <div className="flex gap-16 marquee whitespace-nowrap py-6">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="flex gap-16">
              {[
                { value: "24/7", label: "Atención ininterrumpida" },
                { value: "100%", label: "Leads pre-calificados" },
                { value: "0", label: "Mensajes ignorados" },
                { value: "Automático", label: "Agendamiento y recordatorios" },
              ].map((stat, idx) => (
                <div key={`${idx}-${i}`} className="flex items-baseline gap-4">
                  <span className="text-3xl lg:text-4xl font-display text-primary">{stat.value}</span>
                  <span className="text-sm font-medium text-foreground">{stat.label}</span>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}