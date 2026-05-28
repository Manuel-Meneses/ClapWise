import { Navigation } from "@/components/landing/navigation";
import { HeroSection } from "@/components/landing/hero-section";
import { FeaturesSection } from "@/components/landing/features-section";
import { HowItWorksSection } from "@/components/landing/how-it-works-section";
import { MetricsSection } from "@/components/landing/metrics-section";
import { TeamSection } from "@/components/landing/team-section";
import { PricingSection } from "@/components/landing/pricing-section";
import { CtaSection } from "@/components/landing/cta-section";
import { FooterSection } from "@/components/landing/footer-section";

export default function Home() {
  return (
    // Agregamos bg-white y antialiased para que la tipografía se vea premium (estilo Apple/Stripe)
    <main className="min-h-screen bg-white text-slate-900 selection:bg-emerald-100 selection:text-emerald-900 antialiased font-sans">
      
      {/* 1. Navegación: Transparente y fija */}
      <Navigation />

      {/* 2. Hero: La gran promesa (Resolución de matrices en 3D/Clean) */}
      <HeroSection />

      {/* Separador sutil (Logos de empresas o mensaje de confianza) */}
      <div className="border-y border-slate-100 bg-slate-50/50 py-8 text-center">
        <p className="text-xs font-mono text-slate-400 uppercase tracking-widest font-semibold">
          Metodología analítica protegida bajo estricto Acuerdo de Confidencialidad (NDA)
        </p>
      </div>

      {/* 3. Features: Qué hacemos (La matemática aplicada a los negocios) */}
      <FeaturesSection />

      {/* 4. How It Works: El proceso de cero fricción (El código transparente) */}
      <HowItWorksSection />

      {/* 5. Team: Quiénes somos (El Hacker de FAMAF y el Hustler) */}
      <TeamSection />

      {/* 6. Metrics: Pruebas matemáticas de nuestro impacto */}
      <MetricsSection />

      {/* 7. Pricing: Cuánto cuesta (El Setup y la Recurrencia) */}
      <PricingSection />

      {/* 8. CTA: El empujón final humanizado (De emprendedores a emprendedores) */}
      <CtaSection />

      {/* 9. Footer: Enlaces institucionales */}
      <FooterSection />
      
    </main>
  );
}