"use client";

import { useEffect, useRef, useState } from "react";
import { CheckCircle2, ChevronRight, TerminalSquare } from "lucide-react";

const steps = [
  {
    number: "I",
    title: "Traducción al Espacio Vectorial",
    description: "Tomamos tu Excel desordenado de ventas y lo convertimos en una matriz matemática pura. Cada producto, cliente y horario se vuelve una dimensión calculable.",
    codeLines: [
      { text: "import pandas as pd", type: "keyword" },
      { text: "import numpy as np", type: "keyword" },
      { text: "# Ingesta de datos protegidos por NDA", type: "comment" },
      { text: "df = pd.read_excel('historial_ventas.xlsx')", type: "code" },
      { text: "print(f'Matriz A ∈ R^({len(df)}×{len(df.columns)}) preparada')", type: "string" },
      { text: "> [SISTEMA] Entropía reducida al 0%. Matriz lista.", type: "success" }
    ],
  },
  {
    number: "II",
    title: "Aislamiento de Patrones",
    description: "Calculamos la similitud exacta entre tus mejores compradores y el resto de tu base de datos mediante álgebra lineal, aislando clones conductuales para promociones.",
    codeLines: [
      { text: "from sklearn.metrics.pairwise import cosine_similarity", type: "keyword" },
      { text: "# Cálculo del ángulo θ entre vectores de clientes", type: "comment" },
      { text: "u = vector_cliente_ideal", type: "code" },
      { text: "v = matriz_compradores", type: "code" },
      { text: "similitud = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))", type: "code" },
      { text: "> [SISTEMA] 50 clones de alta rentabilidad aislados.", type: "success" }
    ],
  },
  {
    number: "III",
    title: "Optimización de Rentabilidad",
    description: "Modelamos tus restricciones (stock, personal) como inecuaciones. Nuestro código encuentra el vértice exacto en ese sistema que maximiza tu ganancia neta.",
    codeLines: [
      { text: "from scipy.optimize import linprog", type: "keyword" },
      { text: "# Max Z = c^T x (Sujeto a Ax ≤ b)", type: "comment" },
      { text: "resultado = linprog(-c, A_ub=A, b_ub=b, method='highs')", type: "code" },
      { text: "print('Vértice óptimo localizado')", type: "string" },
      { text: "==========================================", type: "comment" },
      { text: "> [ÉXITO] +18.4% de margen de ganancia proyectado.", type: "success" }
    ],
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
    }, 6000); 
    return () => clearInterval(interval);
  }, []);

  return (
    <section id="how-it-works" ref={sectionRef} className="relative py-24 lg:py-32 bg-slate-50 text-slate-900 overflow-hidden border-y border-slate-200">
      <div className="absolute inset-0 bg-[radial-gradient(#e2e8f0_1px,transparent_1px)] [background-size:24px_24px] opacity-50 pointer-events-none" />

      <div className="relative z-10 max-w-[1400px] mx-auto px-6 lg:px-12">
        <div className="mb-16 lg:mb-24">
          <span className="inline-flex items-center gap-3 text-sm font-mono text-emerald-600 font-semibold uppercase tracking-widest mb-6">
            <span className="w-8 h-px bg-emerald-600" />
            El Motor Analítico
          </span>
          <h2 className={`text-4xl lg:text-6xl font-display tracking-tight transition-all duration-700 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            Tu negocio no es magia.<br />
            <span className="text-slate-400">Es un sistema de ecuaciones por resolver.</span>
          </h2>
        </div>

        <div className="grid lg:grid-cols-2 gap-16 lg:gap-24">
          
          {/* Lado Izquierdo: Pasos */}
          <div className="space-y-0">
            {steps.map((step, index) => (
              <button
                key={step.number}
                type="button"
                onClick={() => setActiveStep(index)}
                className={`w-full text-left py-8 border-b border-slate-200 transition-all duration-500 group ${activeStep === index ? "opacity-100" : "opacity-40 hover:opacity-70"}`}
              >
                <div className="flex items-start gap-6">
                  <span className="font-display text-3xl text-emerald-600">{step.number}</span>
                  <div className="flex-1">
                    <h3 className="text-2xl lg:text-3xl font-display mb-3 text-slate-900 group-hover:translate-x-2 transition-transform duration-300">
                      {step.title}
                    </h3>
                    <p className="text-slate-600 leading-relaxed text-lg font-light">
                      {step.description}
                    </p>
                    {activeStep === index && (
                      <div className="mt-4 h-px bg-slate-200 overflow-hidden">
                        <div className="h-full bg-emerald-500 w-0" style={{ animation: 'progress 6s linear forwards' }} />
                      </div>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Lado Derecho: Entorno de Código Claro (Estilo Jupyter) */}
          <div className="lg:sticky lg:top-32 self-start">
            <div className="border border-slate-200 rounded-2xl overflow-hidden bg-white shadow-[0_20px_60px_-15px_rgba(0,0,0,0.05)] hardware-accelerated">
              
              {/* Header de la ventana */}
              <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-slate-300" />
                  <div className="w-3 h-3 rounded-full bg-slate-300" />
                  <div className="w-3 h-3 rounded-full bg-slate-300" />
                </div>
                <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
                  <TerminalSquare className="w-3 h-3" />
                  clapwise_engine.ipynb
                </div>
              </div>

              {/* Cuerpo del código (Animación optimizada por línea) */}
              <div className="p-8 font-mono text-sm min-h-[340px] bg-white">
                <div className="flex flex-col gap-2">
                  {steps[activeStep].codeLines.map((line, lineIndex) => {
                    // Colores de sintaxis para modo claro
                    let colorClass = "text-slate-600";
                    if (line.type === "keyword") colorClass = "text-blue-600 font-semibold";
                    if (line.type === "comment") colorClass = "text-slate-400 italic";
                    if (line.type === "string") colorClass = "text-amber-600";
                    if (line.type === "success") colorClass = "text-emerald-600 font-bold bg-emerald-50 px-2 py-1 rounded w-fit mt-2 border border-emerald-100";

                    return (
                      <div 
                        key={`${activeStep}-${lineIndex}`} 
                        className={`leading-relaxed code-line-reveal ${colorClass}`} 
                        style={{ animationDelay: `${lineIndex * 150}ms` }}
                      >
                        {line.text}
                      </div>
                    );
                  })}
                </div>
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
        .hardware-accelerated {
          transform: translateZ(0);
          will-change: transform;
          backface-visibility: hidden;
        }
        /* Animación fluida por línea, ya no por letra (Chrome lo agradece) */
        .code-line-reveal {
          opacity: 0;
          transform: translateY(8px);
          animation: fadeUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) forwards;
          will-change: transform, opacity;
        }
        @keyframes fadeUp {
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </section>
  );
}