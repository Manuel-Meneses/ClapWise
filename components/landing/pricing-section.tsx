"use client";

import { ArrowRight, Check } from "lucide-react";

const plans = [
  {
    name: "Filtro Base",
    description: "Para clínicas y negocios locales que quieren dejar de perder mensajes.",
    price: { setup: 199, monthly: 79 },
    features: [
      "Diseño de flujo de conversación",
      "Filtro de 3 preguntas clave",
      "Exportación de Leads a Google Sheets",
      "Soporte técnico por correo",
    ],
    cta: "Comenzar",
    popular: false,
  },
  {
    name: "Ecosistema ClapWise",
    description: "Para empresas con alto volumen que necesitan agendar automáticamente.",
    price: { setup: 499, monthly: 150 },
    features: [
      "Todo lo incluido en Base",
      "Sincronización con Google Calendar",
      "Respuestas con IA entrenada en tu negocio",
      "Alertas a tu celular de 'Leads Calientes'",
      "Soporte prioritario WhatsApp",
    ],
    cta: "Hablar con un asesor",
    popular: true,
  }
];

export function PricingSection() {
  return (
    <section id="pricing" className="relative py-32 lg:py-40 bg-muted/30 border-t border-border">
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <div className="max-w-3xl mb-20">
          <span className="font-mono text-xs tracking-widest text-primary font-bold uppercase block mb-6">
            Inversión Transparente
          </span>
          <h2 className="font-display text-5xl md:text-6xl tracking-tight text-foreground mb-6">
            No pagues por software.<br />
            Paga por <span className="text-primary">resultados.</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-xl">
            Un modelo simple: un costo de instalación por la arquitectura, y un pequeño mantenimiento por tener tu negocio operativo 24/7.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {plans.map((plan, idx) => (
            <div
              key={plan.name}
              className={`relative p-8 lg:p-12 rounded-2xl bg-background shadow-sm transition-all hover:shadow-md ${
                plan.popular ? "border-2 border-primary scale-[1.02]" : "border border-border"
              }`}
            >
              {plan.popular && (
                <span className="absolute -top-3 left-8 px-4 py-1 bg-accent text-white text-xs font-bold uppercase tracking-widest rounded-full shadow-sm">
                  Más Recomendado
                </span>
              )}

              <div className="mb-8">
                <h3 className="font-display text-3xl text-foreground mt-2">{plan.name}</h3>
                <p className="text-sm text-muted-foreground mt-2">{plan.description}</p>
              </div>

              <div className="mb-8 pb-8 border-b border-border flex flex-col gap-3">
                <div className="flex items-baseline gap-2">
                  <span className="text-sm font-medium text-muted-foreground w-24">Setup:</span>
                  <span className="font-display text-4xl text-foreground">${plan.price.setup}</span>
                  <span className="text-sm text-muted-foreground">USD (Único)</span>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-sm font-medium text-muted-foreground w-24">Sistema:</span>
                  <span className="font-display text-2xl text-primary">${plan.price.monthly}</span>
                  <span className="text-sm text-muted-foreground">USD /mes</span>
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

              <button
                className={`w-full py-4 rounded-lg flex items-center justify-center gap-2 text-sm font-bold transition-all group ${
                  plan.popular
                    ? "bg-primary text-white hover:bg-primary/90 shadow-md"
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