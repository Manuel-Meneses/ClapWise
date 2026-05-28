"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { ArrowRight, ShieldCheck, Activity } from "lucide-react";

const words = ["márgenes", "ganancias", "eficiencia", "ventas"];

export function HeroSection() {
  const [isVisible, setIsVisible] = useState(false);
  const [wordIndex, setWordIndex] = useState(0);

  useEffect(() => {
    setIsVisible(true);
    const interval = setInterval(() => {
      setWordIndex((prev) => (prev + 1) % words.length);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative min-h-screen flex flex-col overflow-hidden pt-32 lg:pt-48 pb-20">
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-20">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
      </div>
      
      <div className="relative z-10 max-w-[1400px] mx-auto px-6 lg:px-12 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          
          {/* Columna Izquierda: Texto Comercial */}
          <div className="flex flex-col">
            <div className={`mb-8 transition-all duration-700 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
              <span className="inline-flex items-center gap-3 text-sm font-mono text-primary font-bold tracking-widest uppercase">
                <span className="w-8 h-px bg-primary" />
                Ingeniería de Datos para E-commerce y Retail
              </span>
            </div>
            
            <div className="mb-8">
              <h1 className={`text-[clamp(2.5rem,6vw,5rem)] font-display leading-[1.05] tracking-tight transition-all duration-1000 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}>
                <span className="block text-foreground">Encontramos el dinero</span>
                <span className="block text-muted-foreground">que tu negocio pierde.</span>
                <span className="block mt-2 text-[clamp(1.5rem,4vw,3.5rem)]">
                  Multiplica tus{" "}
                  <span className="relative inline-block text-primary">
                    <span key={wordIndex} className="inline-flex">
                      {words[wordIndex].split("").map((char, i) => (
                        <span key={`${wordIndex}-${i}`} className="inline-block animate-char-in" style={{ animationDelay: `${i * 40}ms` }}>
                          {char}
                        </span>
                      ))}
                    </span>
                    <span className="absolute -bottom-2 left-0 right-0 h-1 bg-primary/20" />
                  </span>
                </span>
              </h1>
            </div>
            
            <div className={`transition-all duration-700 delay-200 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
              <p className="text-xl text-muted-foreground leading-relaxed max-w-xl mb-8">
                Aplicamos álgebra lineal a tu historial de ventas. Sin integraciones complejas ni accesos a tus cuentas. Te mostramos los puntos ciegos de tu inventario en 48 horas.
              </p>
              
              <div className="flex flex-col sm:flex-row items-center gap-4">
                <Button size="lg" className="bg-primary hover:bg-primary/90 text-white shadow-lg shadow-primary/20 px-8 h-14 text-base rounded-full group w-full sm:w-auto">
                  Solicitar Diagnóstico Gratuito
                  <ArrowRight className="w-4 h-4 ml-2 transition-transform group-hover:translate-x-1" />
                </Button>
                <span className="flex items-center gap-2 text-sm text-muted-foreground font-mono">
                  <ShieldCheck className="w-4 h-4 text-green-600" />
                  Protegido por NDA
                </span>
              </div>
            </div>
          </div>

          {/* Columna Derecha: Tarjeta de Optimización Matemática */}
          <div className={`relative flex justify-center items-center transition-all duration-1000 delay-300 ${isVisible ? "opacity-100 translate-x-0" : "opacity-0 translate-x-12"}`}>
            <div className="relative w-full max-w-[500px] aspect-[4/3] rounded-2xl border border-border bg-background/50 backdrop-blur-xl shadow-2xl overflow-hidden flex flex-col">
              {/* Header de la tarjeta */}
              <div className="h-12 border-b border-border bg-muted/30 flex items-center px-4 justify-between">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                  <div className="w-3 h-3 rounded-full bg-green-500/80" />
                </div>
                <div className="font-mono text-xs text-muted-foreground flex items-center gap-2">
                  <Activity className="w-3 h-3 text-primary animate-pulse" />
                  Optimización Activa
                </div>
              </div>
              
              {/* Cuerpo de la tarjeta: Representación Matricial */}
              <div className="flex-1 p-8 flex flex-col justify-center items-center relative">
                <div className="absolute inset-0 bg-primary/5 blur-[80px]" />
                
                <div className="font-serif italic text-3xl md:text-4xl text-foreground flex items-center gap-4 z-10">
                  <span className="text-primary not-italic font-bold tracking-tighter">max</span>
                  <span>Z = </span>
                  <span className="font-bold">c</span>
                  <sup className="text-sm -ml-2 mt-[-15px]">T</sup>
                  <span className="font-bold">x</span>
                </div>

                <div className="mt-8 font-serif text-lg md:text-xl text-muted-foreground z-10 flex items-center gap-4">
                  <span className="italic">sujeto a</span>
                  <div className="flex items-center text-foreground">
                    <span className="text-4xl font-light mr-2">[</span>
                    <div className="flex flex-col text-sm text-center gap-1 font-mono">
                      <span>2.5 &nbsp; 1.0</span>
                      <span>1.0 &nbsp; 3.2</span>
                    </div>
                    <span className="text-4xl font-light ml-2">]</span>
                  </div>
                  <div className="flex flex-col text-sm text-center gap-1 font-mono text-foreground font-bold">
                    <span>x₁</span>
                    <span>x₂</span>
                  </div>
                  <span>≤</span>
                  <div className="flex flex-col text-sm text-center gap-1 font-mono text-primary font-bold">
                    <span>450</span>
                    <span>320</span>
                  </div>
                </div>

                <div className="mt-8 px-4 py-2 rounded-md bg-green-500/10 border border-green-500/20 text-green-400 font-mono text-sm z-10">
                  Vértice óptimo encontrado: Ganancia +18.4%
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}