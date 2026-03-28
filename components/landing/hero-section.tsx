"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { AnimatedSphere } from "./animated-sphere";

const words = ["create", "build", "scale", "ship"];

export function HeroSection() {
  const [isVisible, setIsVisible] = useState(false);
  const [wordIndex, setWordIndex] = useState(0);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setWordIndex((prev) => (prev + 1) % words.length);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    // Se añade pt-32 y lg:pt-48 para mantener distancia con el navbar
    <section className="relative min-h-screen flex flex-col overflow-hidden pt-32 lg:pt-48 pb-20">
      
      {/* Líneas de fondo sutiles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-30">
        {[...Array(8)].map((_, i) => (
          <div
            key={`h-${i}`}
            className="absolute h-px bg-foreground/10"
            style={{
              top: `${12.5 * (i + 1)}%`,
              left: 0,
              right: 0,
            }}
          />
        ))}
        {[...Array(12)].map((_, i) => (
          <div
            key={`v-${i}`}
            className="absolute w-px bg-foreground/10"
            style={{
              left: `${8.33 * (i + 1)}%`,
              top: 0,
              bottom: 0,
            }}
          />
        ))}
      </div>
      
      <div className="relative z-10 max-w-[1400px] mx-auto px-6 lg:px-12 w-full">
        {/* Contenedor Grid: Texto a la izquierda, Visual a la derecha */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          
          {/* Columna Izquierda: Texto */}
          <div className="flex flex-col">
            {/* Eyebrow */}
            <div 
              className={`mb-8 transition-all duration-700 ${
                isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
              }`}
            >
              <span className="inline-flex items-center gap-3 text-sm font-mono text-muted-foreground">
                <span className="w-8 h-px bg-foreground/30" />
                The platform for modern teams
              </span>
            </div>
            
            {/* Main headline */}
            <div className="mb-8">
              <h1 
                className={`text-[clamp(2.5rem,8vw,6rem)] font-display leading-[1] tracking-tight transition-all duration-1000 ${
                  isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
                }`}
              >
                <span className="block">The platform</span>
                <span className="block">
                  to{" "}
                  <span className="relative inline-block">
                    <span 
                      key={wordIndex}
                      className="inline-flex"
                    >
                      {words[wordIndex].split("").map((char, i) => (
                        <span
                          key={`${wordIndex}-${i}`}
                          className="inline-block animate-char-in"
                          style={{
                            animationDelay: `${i * 50}ms`,
                          }}
                        >
                          {char}
                        </span>
                      ))}
                    </span>
                    <span className="absolute -bottom-2 left-0 right-0 h-3 bg-foreground/10" />
                  </span>
                </span>
              </h1>
            </div>
            
            {/* Description */}
            <div className={`transition-all duration-700 delay-200 ${
              isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
            }`}>
              <p className="text-xl text-muted-foreground leading-relaxed max-w-xl mb-10">
                Your toolkit to stop configuring and start innovating. 
                Securely build, deploy, and scale the best experiences.
              </p>
              
              {/* CTAs */}
              <div className="flex flex-col sm:flex-row items-start gap-4">
                <Button 
                  size="lg" 
                  className="bg-foreground hover:bg-foreground/90 text-background px-8 h-14 text-base rounded-full group w-full sm:w-auto"
                >
                  Start free trial
                  <ArrowRight className="w-4 h-4 ml-2 transition-transform group-hover:translate-x-1" />
                </Button>
                <Button 
                  size="lg" 
                  variant="outline" 
                  className="h-14 px-8 text-base rounded-full border-foreground/20 hover:bg-foreground/5 w-full sm:w-auto"
                >
                  Watch demo
                </Button>
              </div>
            </div>
          </div>

          {/* Columna Derecha: Elemento Visual (Celular / AnimatedSphere) */}
          <div 
            className={`relative flex justify-center items-center transition-all duration-1000 delay-300 ${
              isVisible ? "opacity-100 translate-x-0" : "opacity-0 translate-x-12"
            }`}
          >
            <div className="w-full aspect-square max-w-[500px] lg:max-w-[700px] relative">
              {/* Resplandor de fondo para el visual */}
              <div className="absolute inset-0 bg-foreground/5 blur-[120px] rounded-full" />
              <AnimatedSphere />
            </div>
          </div>
        </div>
      </div>
      
      {/* Stats marquee - Ajustado para no interferir con el grid */}
      <div 
        className={`mt-24 transition-all duration-700 delay-500 ${
          isVisible ? "opacity-100" : "opacity-0"
        }`}
      >
        <div className="flex gap-16 marquee whitespace-nowrap border-y border-foreground/5 py-8">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="flex gap-16">
              {[
                { value: "20 days", label: "saved on builds", company: "NETFLIX" },
                { value: "98%", label: "faster deployment", company: "STRIPE" },
                { value: "300%", label: "throughput increase", company: "LINEAR" },
                { value: "6x", label: "faster to ship", company: "NOTION" },
              ].map((stat) => (
                <div key={`${stat.company}-${i}`} className="flex items-baseline gap-4">
                  <span className="text-4xl lg:text-5xl font-display">{stat.value}</span>
                  <span className="text-sm text-muted-foreground">
                    {stat.label}
                    <span className="block font-mono text-xs mt-1">{stat.company}</span>
                  </span>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}