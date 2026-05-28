"use client";

import { useEffect, useRef, useState } from "react";

const steps = [
  {
    number: "I",
    title: "Traducción al Espacio Vectorial",
    description: "Firmamos el NDA para blindar tus datos. Luego, tomamos tu Excel desordenado de ventas y lo convertimos en una matriz matemática pura. Cada producto, cliente y horario se vuelve una dimensión calculable.",
    code: `DEFINIENDO_ESPACIO_VECTORIAL...\n\n> Sea A ∈ R^(m×n) la matriz comercial\n> m = 4500 (transacciones)\n> n = 12 (características operativas)\n\n      [ x_11  x_12 ... x_1n ]\n  A = [  ...   ... ...  ... ]\n      [ x_m1  x_m2 ... x_mn ]\n\n[✓] Datos estructurados sin ruido`,
  },
  {
    number: "II",
    title: "Aislamiento de Patrones",
    description: "No hacemos suposiciones demográficas. Usamos álgebra lineal para calcular la similitud exacta entre tus mejores compradores y el resto de tu base de datos, aislando clones conductuales para tus promociones.",
    code: `PROCESANDO_SIMILITUD_CONDUCTUAL...\n\n> Proyección de cliente ideal (u)\n> Calculando producto escalar en R^n:\n\n  cos(θ) = (u · v) / (||u|| ||v||)\n\n> Aislando vectores con θ < 0.05 rad\n\n[✓] 50 clones de alta rentabilidad detectados`,
  },
  {
    number: "III",
    title: "Optimización de la Función Objetivo",
    description: "Modelamos tus restricciones reales (stock, horas de personal, presupuesto) como inecuaciones. Nuestro código encuentra el vértice exacto en ese sistema que maximiza tu margen de ganancia neta.",
    code: `MAXIMIZANDO_FUNCION_OBJETIVO...\n\n> Restricciones: A_ub · x ≤ b_ub\n> Función de ganancia (Z):\n\n  max Z = c^T · x\n\n> Calculando vértices del politopo...\n\n[✓] PUNTO ÓPTIMO ALCANZADO\n[!] $3,250 USD extra proyectados / mes`,
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
    }, 6000); // Aumentado a 6s para que el usuario pueda "leer" la matemática
    return () => clearInterval(interval);
  }, []);

  return (
    <section id="how-it-works" ref={sectionRef} className="relative py-24 lg:py-32 bg-foreground text-background overflow-hidden">
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none">
        <div className="absolute inset-0" style={{ backgroundImage: `repeating-linear-gradient(-45deg, transparent, transparent 40px, currentColor 40px, currentColor 41px)` }} />
      </div>

      <div className="relative z-10 max-w-[1400px] mx-auto px-6 lg:px-12">
        <div className="mb-16 lg:mb-24">
          <span className="inline-flex items-center gap-3 text-sm font-mono text-background/60 tracking-widest uppercase mb-6">
            <span className="w-8 h-px bg-background/50" />
            El Motor Matemático
          </span>
          <h2 className={`text-4xl lg:text-6xl font-display tracking-tight transition-all duration-700 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            Tu negocio no es magia.<br />
            <span className="text-background/50">Es un sistema de ecuaciones por resolver.</span>
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
                className={`w-full text-left py-8 border-b border-background/10 transition-all duration-500 group ${activeStep === index ? "opacity-100" : "opacity-40 hover:opacity-70"}`}
              >
                <div className="flex items-start gap-6">
                  <span className="font-display text-3xl text-primary">{step.number}</span>
                  <div className="flex-1">
                    <h3 className="text-2xl lg:text-3xl font-display mb-3 group-hover:translate-x-2 transition-transform duration-300">
                      {step.title}
                    </h3>
                    <p className="text-background/70 leading-relaxed text-lg">
                      {step.description}
                    </p>
                    {activeStep === index && (
                      <div className="mt-4 h-px bg-background/20 overflow-hidden">
                        <div className="h-full bg-primary w-0" style={{ animation: 'progress 6s linear forwards' }} />
                      </div>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Lado derecho: Terminal Matemática */}
          <div className="lg:sticky lg:top-32 self-start">
            <div className="border border-background/20 rounded-xl overflow-hidden bg-[#0A192F] shadow-2xl">
              <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between bg-black/40">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>
                <span className="text-xs font-mono text-white/50">core_algebra_engine.py</span>
              </div>

              <div className="p-8 font-mono text-sm min-h-[340px] text-emerald-400 bg-black/60">
                <pre className="whitespace-pre-wrap">
                  {steps[activeStep].code.split('\n').map((line, lineIndex) => (
                    <div key={`${activeStep}-${lineIndex}`} className="leading-loose code-line-reveal" style={{ animationDelay: `${lineIndex * 40}ms` }}>
                      <span className="inline-flex">
                        {line.split('').map((char, charIndex) => (
                          <span key={`${activeStep}-${lineIndex}-${charIndex}`} className="code-char-reveal" style={{ animationDelay: `${lineIndex * 40 + charIndex * 10}ms` }}>
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
          animation: lineReveal 0.3s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        }
        @keyframes lineReveal {
          to { opacity: 1; transform: translateX(0); }
        }
        .code-char-reveal {
          opacity: 0;
          filter: blur(8px);
          animation: charReveal 0.2s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        }
        @keyframes charReveal {
          to { opacity: 1; filter: blur(0); }
        }
      `}</style>
    </section>
  );
}