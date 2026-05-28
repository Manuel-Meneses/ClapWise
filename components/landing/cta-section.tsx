"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { ArrowRight, Calculator, HeartHandshake } from "lucide-react";

export function CtaSection() {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setIsVisible(true);
      },
      { threshold: 0.2 }
    );

    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section ref={sectionRef} className="relative py-24 lg:py-32 overflow-hidden bg-white border-t border-slate-100">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
        <div
          className={`relative border border-slate-200 bg-white rounded-3xl transition-all duration-1000 shadow-[0_20px_60px_-15px_rgba(0,0,0,0.05)] ${
            isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
          }`}
        >
          {/* Fondo cálido sutil */}
          <div className="absolute top-0 right-0 w-full h-full overflow-hidden rounded-3xl pointer-events-none">
            <div className="absolute -top-[50%] -right-[10%] w-[50%] h-[100%] rounded-full bg-emerald-50 blur-[120px] opacity-80" />
            <div className="absolute -bottom-[50%] -left-[10%] w-[50%] h-[100%] rounded-full bg-blue-50 blur-[120px] opacity-80" />
          </div>
          
          <div className="relative z-10 px-8 lg:px-16 py-16 lg:py-24 grid lg:grid-cols-2 gap-16 items-center">
            
            {/* Columna Izquierda: El Lado Humano */}
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100/50 border border-emerald-200 text-emerald-700 text-sm font-medium mb-8">
                <HeartHandshake className="w-4 h-4" />
                De emprendedores para emprendedores
              </div>
              
              <h2 className="text-4xl lg:text-6xl font-display tracking-tight text-slate-900 mb-6 leading-[1.05]">
                Detrás de cada matriz, hay un negocio que <span className="text-emerald-600 italic">cuesta mantener.</span>
              </h2>

              <p className="text-xl text-slate-600 mb-6 leading-relaxed font-light">
                Sabemos que administrar una Pyme es agotador. El estrés de pagar sueldos, el capital atrapado en stock que no se vende y la sensación de que trabajas más horas para ganar lo mismo.
              </p>
              
              <p className="text-xl text-slate-600 mb-10 leading-relaxed font-light">
                Nuestra matemática no busca reemplazarte. Busca ordenarte, darte tranquilidad mental a fin de mes y devolverte el tiempo que tu negocio te está robando.
              </p>

              <div className="flex flex-col sm:flex-row items-center gap-4">
                <Button size="lg" className="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-600/20 px-8 h-14 text-base rounded-full group transition-all">
                  Solicitar Auditoría sin costo
                  <ArrowRight className="w-4 h-4 ml-2 transition-transform group-hover:translate-x-1" />
                </Button>
              </div>
            </div>

            {/* Columna Derecha: Resumen de Valor (Baja Fricción) */}
            <div className="relative">
              <div className="bg-slate-50 border border-slate-200 rounded-2xl p-8 lg:p-10 shadow-sm relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500" />
                
                <h3 className="font-display text-2xl text-slate-900 mb-6 flex items-center gap-3">
                  <Calculator className="w-6 h-6 text-emerald-600" />
                  El trato es simple:
                </h3>
                
                <ul className="space-y-6">
                  <li className="flex items-start gap-4">
                    <div className="w-8 h-8 rounded-full bg-white border border-slate-200 flex items-center justify-center shrink-0 font-mono text-sm font-bold text-slate-900 shadow-sm">1</div>
                    <div>
                      <h4 className="font-bold text-slate-900">Firmamos Confidencialidad</h4>
                      <p className="text-slate-600 text-sm mt-1">Antes de ver un solo número, tus datos quedan protegidos legalmente.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-4">
                    <div className="w-8 h-8 rounded-full bg-white border border-slate-200 flex items-center justify-center shrink-0 font-mono text-sm font-bold text-slate-900 shadow-sm">2</div>
                    <div>
                      <h4 className="font-bold text-slate-900">Mandas tu Excel de Ventas</h4>
                      <p className="text-slate-600 text-sm mt-1">Sin pedirte claves, ni conectarnos a tu banco o sistema de AFIP.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-4">
                    <div className="w-8 h-8 rounded-full bg-emerald-100 border border-emerald-200 flex items-center justify-center shrink-0 font-mono text-sm font-bold text-emerald-700 shadow-sm">3</div>
                    <div>
                      <h4 className="font-bold text-emerald-700">Te mostramos dónde pierdes dinero</h4>
                      <p className="text-slate-600 text-sm mt-1">Te entregamos un reporte en 48hs. Si no te sirve, no pagas nada. Si te sirve, charlamos.</p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>

          </div>
        </div>
      </div>
    </section>
  );
}