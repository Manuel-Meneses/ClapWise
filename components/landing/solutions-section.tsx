"use client";

import { useEffect, useRef, useState } from "react";
import { CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

const solutions = [
  {
    title: "Clínicas y Consultorios",
    description: "Acaba con el teléfono sonando sin parar y los turnos vacíos por cancelaciones.",
    image: "https://images.unsplash.com/photo-1581056771107-24ca5f033842?auto=format&fit=crop&w=800&q=80",
    benefits: [
      "Agendamiento de turnos 24/7",
      "Filtro por obra social o particular",
      "Recordatorios automáticos por WhatsApp"
    ]
  },
  {
    title: "Agencias Inmobiliarias",
    description: "Filtra a los curiosos de los verdaderos compradores antes de mostrar una propiedad.",
    image: "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=800&q=80",
    benefits: [
      "Clasificación automática (Comprar/Alquilar)",
      "Envío de catálogos en PDF al instante",
      "Sincronización de leads con tu CRM"
    ]
  },
  {
    title: "Talleres y Servicios",
    description: "Da presupuestos base y coordina ingresos sin interrumpir el trabajo en el taller.",
    image: "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?auto=format&fit=crop&w=800&q=80",
    benefits: [
      "Cotizaciones automáticas estándar",
      "Recepción de fotos del problema",
      "Aviso automático de 'Trabajo Terminado'"
    ]
  }
];

export function SolutionsSection() {
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

  return (
    <section id="solutions" ref={sectionRef} className="relative py-24 lg:py-32 bg-background">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
        <div className="mb-16 lg:mb-24 text-center max-w-3xl mx-auto">
          <span className="inline-flex items-center gap-3 text-sm font-mono text-primary font-semibold mb-6">
            <span className="w-8 h-px bg-primary" />
            Casos de Uso
            <span className="w-8 h-px bg-primary" />
          </span>
          <h2 className={`text-4xl lg:text-5xl font-display tracking-tight text-foreground transition-all duration-700 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            Sistemas adaptados a <br />
            <span className="text-secondary">la realidad de tu rubro.</span>
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {solutions.map((solution, index) => (
            <div 
              key={solution.title}
              className={cn(
                "group rounded-2xl border border-border bg-card overflow-hidden shadow-sm hover:shadow-md transition-all duration-500 flex flex-col",
                isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-12"
              )}
              style={{ transitionDelay: `${index * 150}ms` }}
            >
              <div className="relative h-48 w-full overflow-hidden">
                <img 
                  src={solution.image} 
                  alt={solution.title}
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                <h3 className="absolute bottom-4 left-6 text-2xl font-display text-white">
                  {solution.title}
                </h3>
              </div>
              <div className="p-6 flex flex-col flex-1">
                <p className="text-muted-foreground mb-6">
                  {solution.description}
                </p>
                <ul className="space-y-3 mt-auto">
                  {solution.benefits.map((benefit) => (
                    <li key={benefit} className="flex items-start gap-2">
                      <CheckCircle2 className="w-5 h-5 text-primary shrink-0" />
                      <span className="text-sm text-foreground">{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}