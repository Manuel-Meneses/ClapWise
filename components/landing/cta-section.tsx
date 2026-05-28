"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

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
    <section ref={sectionRef} className="relative py-24 lg:py-32 overflow-hidden bg-background">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
        <div
          className={`relative rounded-3xl border border-border bg-muted/20 overflow-hidden transition-all duration-1000 ${
            isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
          }`}
        >
          <div className="relative z-10 px-8 lg:px-16 py-16 lg:py-24">
            <div className="flex flex-col lg:flex-row items-center justify-between gap-12">
              
              {/* Left content */}
              <div className="flex-1">
                <h2 className="text-4xl lg:text-6xl font-display tracking-tight text-foreground mb-8 leading-[1.1]">
                  ¿Listo para escalar
                  <br />
                  <span className="text-primary">sin trabajar más horas?</span>
                </h2>

                <p className="text-xl text-muted-foreground mb-12 leading-relaxed max-w-xl">
                  Agenda una videollamada de 15 minutos. Te mostraremos un sistema en vivo funcionando para un negocio idéntico al tuyo.
                </p>

                <div className="flex flex-col sm:flex-row items-start gap-4">
                  <Button size="lg" className="bg-primary hover:bg-primary/90 text-white shadow-lg shadow-primary/25 px-8 h-14 text-base rounded-full group">
                    Agendar reunión ahora
                    <ArrowRight className="w-4 h-4 ml-2 transition-transform group-hover:translate-x-1" />
                  </Button>
                </div>
              </div>

              {/* Right Image (Sustituye al Tetraedro) */}
              <div className="hidden lg:block w-full max-w-[400px] aspect-[4/5] rounded-2xl overflow-hidden shadow-xl border border-border transform rotate-2 hover:rotate-0 transition-transform duration-500">
                 <img 
                  src="https://images.unsplash.com/photo-1556761175-4b46a572b786?auto=format&fit=crop&w=800&q=80" 
                  alt="Equipo de trabajo exitoso" 
                  className="w-full h-full object-cover"
                />
              </div>

            </div>
          </div>
        </div>
      </div>
    </section>
  );
}