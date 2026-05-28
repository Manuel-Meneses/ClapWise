"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import { GraduationCap, Briefcase, ChevronRight } from "lucide-react";

export function TeamSection() {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setIsVisible(true);
      },
      { threshold: 0.15 }
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section id="team" ref={sectionRef} className="py-24 bg-white border-t border-slate-100">
      <div className="max-w-[1200px] mx-auto px-6 lg:px-12">
        
        {/* Encabezado Minimalista */}
        <div className={`mb-16 max-w-2xl transition-all duration-700 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
          <h2 className="text-3xl font-display tracking-tight text-slate-900 mb-4">
            El rigor científico se encuentra con la estrategia comercial.
          </h2>
          <p className="text-slate-600 text-lg font-light leading-relaxed">
            Clapwise nace en Córdoba con un objetivo singular: democratizar el nivel de análisis cuantitativo que usan las grandes corporaciones, haciéndolo accesible, seguro y rentable para la Pyme.
          </p>
        </div>

        {/* Grilla de Fundadores (Estilo Y-Combinator / Startup) */}
        <div className="grid md:grid-cols-2 gap-x-12 gap-y-16">
          
          {/* Perfil: Manuel */}
          <div className={`flex flex-col transition-all duration-700 delay-100 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}>
            <div className="flex items-center gap-4 mb-6">
              <div className="relative w-16 h-16 rounded-full overflow-hidden border border-slate-200 bg-slate-50 shrink-0">
                <Image 
                  src="/placeholder-user.jpg" // Tu foto real, fondo neutro
                  alt="Manuel Meneses"
                  fill
                  className="object-cover"
                />
              </div>
              <div>
                <h3 className="text-xl font-display text-slate-900">Manuel Meneses</h3>
                <p className="text-emerald-600 font-mono text-xs font-semibold tracking-wider uppercase">Motor Cuantitativo</p>
              </div>
            </div>
            
            <p className="text-slate-600 font-light leading-relaxed mb-6">
              Responsable de la precisión algorítmica de cada auditoría. Utiliza el modelado matemático para transformar la entropía de los datos de ventas en rutas predecibles de rentabilidad, asegurando que las inecuaciones reflejen la realidad operativa del cliente con cero margen de error.
            </p>

            <div className="flex items-center gap-2 text-sm text-slate-500 font-mono bg-slate-50 px-3 py-2 rounded-md w-fit border border-slate-100">
              <GraduationCap className="w-4 h-4 text-emerald-500" />
              Licenciatura en Física (FAMAF - UNC)
            </div>
          </div>

          {/* Perfil: Socio */}
          <div className={`flex flex-col transition-all duration-700 delay-200 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}>
            <div className="flex items-center gap-4 mb-6">
              <div className="relative w-16 h-16 rounded-full overflow-hidden border border-slate-200 bg-slate-50 shrink-0">
                <Image 
                  src="/placeholder-user.jpg" // Foto real de tu socio
                  alt="Socio"
                  fill
                  className="object-cover"
                />
              </div>
              <div>
                <h3 className="text-xl font-display text-slate-900">Nombre del Socio</h3>
                <p className="text-blue-600 font-mono text-xs font-semibold tracking-wider uppercase">Operaciones & Estrategia</p>
              </div>
            </div>
            
            <p className="text-slate-600 font-light leading-relaxed mb-6">
              El escudo protector de tu información. Garantiza el cumplimiento irrestricto de los Acuerdos de Confidencialidad (NDA) y traduce los hallazgos matriciales en planes de acción ejecutivos. Si el modelo matemático detecta la fuga, él se asegura de que la cierres ese mismo día.
            </p>

            <div className="flex items-center gap-2 text-sm text-slate-500 font-mono bg-slate-50 px-3 py-2 rounded-md w-fit border border-slate-100">
              <Briefcase className="w-4 h-4 text-blue-500" />
              Estructuración de Negocios
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}