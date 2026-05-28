"use client";

import { useEffect, useRef, useState } from "react";
import { BarChart3, Users, ShoppingBag, LineChart, LucideIcon } from "lucide-react";

const features = [
  {
    number: "01",
    title: "Optimización de Inventario (Programación Lineal)",
    description: "Resolvemos sistemas de inecuaciones adaptados a tus restricciones reales de capital, espacio y personal. Determinamos matemáticamente la cantidad exacta de stock a comprar para maximizar el flujo de caja y erradicar el capital inmovilizado.",
    icon: BarChart3,
  },
  {
    number: "02",
    title: "Clonación de Clientes (Similitud del Coseno)",
    description: "Tratamos tu base de datos como un espacio vectorial multidimensional. Al calcular la dirección del comportamiento de tus compradores más rentables, aislamos clones conductuales perfectos en tu lista para dirigir ofertas con máxima probabilidad de conversión.",
    icon: Users,
  },
  {
    number: "03",
    title: "Inteligencia de Combinación (Market Basket Analysis)",
    description: "Analizamos probabilísticamente cada ticket emitido mediante algoritmos de asociación. Descubrimos qué productos se compran juntos de forma invisible para estructurar combos estratégicos que elevan de inmediato tu ticket promedio.",
    icon: ShoppingBag,
  },
  {
    number: "04",
    title: "Reducción de Ruido Comercial (Filtro Dimensional)",
    description: "Reducimos decenas de variables ruidosas a través de transformaciones lineales y análisis de covarianza. Aislamos exclusivamente las variables críticas (como estacionalidad u horarios) que realmente alteran el rumbo de tus ganancias.",
    icon: LineChart,
  },
];

function FeatureCard({ feature, index }: { feature: typeof features[0]; index: number }) {
  const [isVisible, setIsVisible] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);
  const Icon = feature.icon;

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setIsVisible(true);
      },
      { threshold: 0.2 }
    );

    if (cardRef.current) observer.observe(cardRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={cardRef}
      className={`group relative transition-all duration-700 ${
        isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-12"
      }`}
      style={{ transitionDelay: `${index * 100}ms` }}
    >
      <div className="flex flex-col lg:flex-row gap-8 lg:gap-16 py-12 lg:py-16 border-b border-foreground/10">
        {/* Número */}
        <div className="shrink-0">
          <span className="font-mono text-sm text-primary font-bold">{feature.number}</span>
        </div>
        
        {/* Contenido */}
        <div className="flex-1 grid lg:grid-cols-2 gap-8 items-center">
          <div>
            <h3 className="text-2xl lg:text-3xl font-display mb-4 group-hover:translate-x-2 transition-transform duration-500 text-foreground">
              {feature.title}
            </h3>
            <p className="text-lg text-muted-foreground leading-relaxed">
              {feature.description}
            </p>
          </div>
          
          {/* Visual Icon */}
          <div className="flex justify-center lg:justify-end">
            <div className="w-16 h-16 flex items-center justify-center border border-border rounded-xl bg-muted/20 text-primary group-hover:bg-primary group-hover:text-white transition-all duration-500 shadow-sm">
              <Icon size={32} strokeWidth={1.5} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export { FeatureCard };

export function FeaturesSection() {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => { if (entry.isIntersecting) setIsVisible(true); }, { threshold: 0.1 });
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section id="features" ref={sectionRef} className="relative py-24 lg:py-32 bg-background">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
        <div className="mb-16 lg:mb-24">
          <span className="inline-flex items-center gap-3 text-sm font-mono text-primary font-semibold mb-6">
            <span className="w-8 h-px bg-primary" />
            Soluciones Científicas
          </span>
          <h2 className={`text-4xl lg:text-6xl font-display tracking-tight text-foreground transition-all duration-700 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
            Ingeniería de datos avanzada.<br />
            <span className="text-muted-foreground">Estructurada para impactar tu balance neto.</span>
          </h2>
        </div>

        <div>
          {features.map((feature, index) => (
            <FeatureCard key={feature.number} feature={feature} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
}