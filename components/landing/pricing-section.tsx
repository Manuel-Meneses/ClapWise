"use client";

import { ArrowRight, Check } from "lucide-react";

const plans = [
  {
    name: "Auditoría de Fugas",
    description: "Diagnóstico profundo de ineficiencias financieras ocultas utilizando tus datos históricos.",
    price: { setup: 0, monthly: 0 },
    features: [
      "Firma previa de Acuerdo de Confidencialidad (NDA)",
      "Procesamiento y limpieza de hasta 60 días de historial",
      "Modelado matemático de vectores de comportamiento",
      "Identificación exacta de capital estancado en stock",
      "Reporte diagnóstico visual 100% gratuito",
    ],
    cta: "Solicitar Reporte Gratis",
    popular: false,
  },
  {
    name: "Ecosistema Centralizado",
    description: "Despliegue de analítica interactiva y automatización continua para optimización semanal.",
    price: { setup: 249, monthly: 99 },
    features: [
      "Todo lo incluido en la Auditoría Inicial",
      "Diseño y despliegue de tablero privado en Looker Studio",
      "Automatización de carga semanal mediante entorno en la nube",
      "Alertas proactivas de reabastecimiento crítico",
      "Algoritmo dinámico para cálculo de precios óptimos",
      "Sesión de consultoría mensual de 15 minutos (Análisis de ROI)",
    ],
    cta: "Implementar Sistema",
    popular: true,
  }
];

export function PricingSection() {
  return (
    <section id="pricing" className="relative py-32 lg:py-40 bg-muted/10 border-t border-border">
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <div className="max-w-3xl mb-20">
          <span className="font-mono text-xs tracking-widest text-primary font-bold uppercase block mb-6">
            Estructura de Inversión
          </span>
          <h2 className="font-display text-5xl md:text-6xl tracking-tight text-foreground mb-6">
            No cobramos por código.<br />
            Cobramos por <span className="text-primary">capital recuperado.</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-xl">
            Un esquema transparente de baja fricción: demostramos nuestra efectividad con tu pasado antes de integrarnos a tu futuro operativo.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative p-8 lg:p-12 rounded-2xl bg-background shadow-sm transition-all hover:shadow-md flex flex-col justify-between ${
                plan.popular ? "border-2 border-primary scale-[1.02]" : "border border-border"
              }`}
            >
              {plan.popular && (
                <span className="absolute -top-3 left-8 px-4 py-1 bg-primary text-white text-xs font-bold uppercase tracking-widest rounded-full shadow-sm">
                  Plan de Escala
                </span>
              )}

              <div>
                <div className="mb-6">
                  <h3 className="font-display text-3xl text-foreground mt-2">{plan.name}</h3>
                  <p className="text-sm text-muted-foreground mt-2 min-h-[40px]">{plan.description}</p>
                </div>

                <div className="mb-8 pb-6 border-b border-border flex flex-col gap-3">
                  <div className="flex items-baseline gap-2">
                    <span className="text-xs font-mono text-muted-foreground w-16">Setup Fee:</span>
                    <span className="font-display text-3xl text-foreground">${plan.price.setup}</span>
                    <span className="text-xs text-muted-foreground">USD (Pago único)</span>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-xs font-mono text-muted-foreground w-16">Mantenimiento:</span>
                    <span className="font-display text-2xl text-primary">${plan.price.monthly}</span>
                    <span className="text-xs text-muted-foreground">USD / mes</span>
                  </div>
                </div>

                <ul className="space-y-4 mb-10">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3">
                      <Check className="w-5 h-5 text-primary mt-0.5 shrink-0" />
                      <span className="text-sm text-foreground">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <button
                className={`w-full py-4 rounded-lg flex items-center justify-center gap-2 text-sm font-bold transition-all group mt-auto ${
                  plan.popular
                    ? "bg-primary text-white hover:bg-primary/90 shadow-md shadow-primary/10"
                    : "border border-primary text-primary hover:bg-primary/5"
                }`}
              >
                {plan.cta}
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}