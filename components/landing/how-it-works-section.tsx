"use client";

import { useEffect, useRef, useState } from "react";

const steps = [
  {
    number: "I",
    title: "Auditoría de tu negocio",
    description: "Analizamos cómo vendes hoy, qué preguntan tus clientes y diseñamos la arquitectura lógica de tu nuevo asistente virtual.",
    code: `ANALIZANDO_NEGOCIO...
    
> Detectando Preguntas Frecuentes: 100%
> Mapeando Flujo de Ventas: 100%
> Definiendo Perfil de Cliente Ideal

[✓] Arquitectura Lógica Completada`,
  },
  {
    number: "II",
    title: "Construcción del Sistema",
    description: "Conectamos las APIs necesarias (WhatsApp, IA, Calendarios) asegurándonos de que la información fluya sin errores.",
    code: `CONECTANDO_INFRAESTRUCTURA...

> Conexión API WhatsApp: Establecida
> Motor NLP (Procesamiento Lógico): Activo
> Enlace Base de Datos (Sheets/CRM): Sincronizado

[✓] Sistema Listo para Pruebas`,
  },
  {
    number: "III",
    title: "Despliegue y Captación",
    description: "Encendemos el interruptor. Tu número de WhatsApp comienza a atender 24/7 y tú solo abres tu Excel para ver los leads cerrados.",
    code: `MONITOREO_EN_TIEMPO_REAL...

[14:02] Nuevo mensaje recibido
[14:02] IA: Clasificando intención...
[14:03] IA: Filtro superado (Lead Caliente)
[14:03] Acción: Fila añadida en Excel
[14:04] Acción: Turno agendado con éxito

[✓] Venta Recuperada`,
  },
];

export function HowItWorksSection() {
  const [activeStep, setActiveStep] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setIsVisible(true);
      },
      { threshold: 0.1 }
    );

    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % steps.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
<section id="how-it-works" ref={sectionRef} className="relative py-24 lg:py-32 bg-primary text-white overflow-hidden">
      {/* Fondo de líneas diagonales */}
      <div className="absolute inset-0 opacity-[0.05] pointer-events-none">
        <div className="absolute inset-0" style={{ backgroundImage: `repeating-linear-gradient(-45deg, transparent, transparent 40px, currentColor 40px, currentColor 41px)` }} />
      </div>

      <div className="relative z-10 max-w-[1400px] mx-auto px-6 lg:px-12">
        <div className="mb-16 lg:mb-24">
          <span className="inline-flex items-center gap-3 text-sm font-mono text-white/70 font-semibold mb-6">
            <span className="w-8 h-px bg-white/50" />
            Nuestro Proceso
          </span>
          <h2 className={`text-4xl lg:text-6xl font-display tracking-tight transition-all duration-700 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            Del caos al orden.<br />
            <span className="text-secondary">En 3 simples pasos.</span>
          </h2>
        </div>

        <div className="grid lg:grid-cols-2 gap-16 lg:gap-24">
          {/* Lado izquierdo: Pasos */}
          <div className="space-y-0">
            {steps.map((step, index) => (
              <button
                key={step.number}
                type="button"
                onClick={() => setActiveStep(index)}
                className={`w-full text-left py-8 border-b border-white/10 transition-all duration-500 group ${activeStep === index ? "opacity-100" : "opacity-40 hover:opacity-70"}`}
              >
                <div className="flex items-start gap-6">
                  <span className="font-display text-3xl text-secondary">{step.number}</span>
                  <div className="flex-1">
                    <h3 className="text-2xl lg:text-3xl font-display mb-3 group-hover:translate-x-2 transition-transform duration-300">
                      {step.title}
                    </h3>
                    <p className="text-white/80 leading-relaxed">
                      {step.description}
                    </p>
                    {activeStep === index && (
                      <div className="mt-4 h-px bg-white/20 overflow-hidden">
                        <div className="h-full bg-secondary w-0" style={{ animation: 'progress 5s linear forwards' }} />
                      </div>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Lado derecho: Terminal simulada */}
          <div className="lg:sticky lg:top-32 self-start">
            <div className="border border-white/20 rounded-lg overflow-hidden bg-[#0A192F] shadow-2xl">
              <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between bg-black/20">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                  <div className="w-3 h-3 rounded-full bg-green-500/80" />
                </div>
                <span className="text-xs font-mono text-white/50">ClapWise_Engine.exe</span>
              </div>

              <div className="p-8 font-mono text-sm min-h-[280px] text-green-400">
                <pre className="whitespace-pre-wrap">
                  {steps[activeStep].code.split('\n').map((line, lineIndex) => (
                    <div key={`${activeStep}-${lineIndex}`} className="leading-loose code-line-reveal" style={{ animationDelay: `${lineIndex * 80}ms` }}>
                      <span className="inline-flex">
                        {line.split('').map((char, charIndex) => (
                          <span key={`${activeStep}-${lineIndex}-${charIndex}`} className="code-char-reveal" style={{ animationDelay: `${lineIndex * 80 + charIndex * 15}ms` }}>
                            {char === ' ' ? '\u00A0' : char}
                          </span>
                        ))}
                      </span>
                    </div>
                  ))}
                </pre>
              </div>
            </div>
          </div>
        </div>
      </div> 

      <style jsx>{`
        @keyframes progress {
          from { width: 0%; }
          to { width: 100%; }
        }
        
        .code-line-reveal {
          opacity: 0;
          transform: translateX(-8px);
          animation: lineReveal 0.4s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        }
        
        @keyframes lineReveal {
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        .code-char-reveal {
          opacity: 0;
          filter: blur(8px);
          animation: charReveal 0.3s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        }
        
        @keyframes charReveal {
          to {
            opacity: 1;
            filter: blur(0);
          }
        }
      `}</style>
    </section>
  );
}
