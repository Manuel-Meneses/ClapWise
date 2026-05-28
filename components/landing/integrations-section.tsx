"use client";

import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

// Isotipos SVG Reales y Optimizados
const BrandLogos = {
  WhatsApp: () => (
    <svg viewBox="0 0 24 24" className="w-8 h-8 fill-[#25D366]">
      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51a12.8 12.8 0 0 0-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/>
    </svg>
  ),
  GoogleSheets: () => (
    <svg viewBox="0 0 24 24" className="w-8 h-8 fill-[#0F9D58]">
      <path d="M14.016 3H5.984C4.89 3 4 3.89 4 4.984v14.032C4 20.11 4.89 21 5.984 21h12.032c1.094 0 1.984-.89 1.984-1.984V8.984L14.016 3zM16 17H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
    </svg>
  ),
  OpenAI: () => (
    <svg viewBox="0 0 24 24" className="w-8 h-8 fill-foreground">
      <path d="M22.282 9.821a5.985 5.985 0 0 0-.516-4.91 6.046 6.046 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.981 4.18a5.985 5.985 0 0 0-3.998 2.9 6.046 6.046 0 0 0 .743 7.097 5.98 5.98 0 0 0 .51 4.91 6.051 6.051 0 0 0 6.515 2.9 5.985 5.985 0 0 0 4.509 2.013 6.056 6.056 0 0 0 5.471-3.188 5.986 5.986 0 0 0 3.929-2.9 6.056 6.056 0 0 0-.378-8.091Zm-8.922 12.608a4.476 4.476 0 0 1-2.876-1.041l.142-.08 4.778-2.759a.795.795 0 0 0 .393-.681v-6.737l2.02 1.169a.071.071 0 0 1 .038.052v5.583a4.504 4.504 0 0 1-4.495 4.494Zm-9.66-4.125a4.47 4.47 0 0 1-.535-3.014l.142.085 4.783 2.758a.771.771 0 0 0 .78 0l5.843-3.368v2.332a.08.08 0 0 1-.033.061L9.74 19.95a4.5 4.5 0 0 1-6.04-1.646Zm1.646-10.45A4.47 4.47 0 0 1 7.684 5.86l-.085.142-2.758 4.783a.771.771 0 0 0 0 .78l3.368 5.843H5.877a.08.08 0 0 1-.061-.033L2.616 11.238A4.5 4.5 0 0 1 4.263 5.196Zm11.831 1.04a4.476 4.476 0 0 1 2.876 1.04l-.142.08-4.778 2.758a.795.795 0 0 0-.393.681v6.737l-2.02-1.169a.071.071 0 0 1-.038-.052V6.737a4.504 4.504 0 0 1 4.495-4.494Zm-1.884 7.642L12 12.508l-2.21-1.275 2.21-1.275 2.21 1.275v2.55Zm5.527-4.922a4.47 4.47 0 0 1-2.339 1.993l.085-.142 2.758-4.783a.771.771 0 0 0 0-.78l-3.368-5.843h2.332a.08.08 0 0 1 .061.033l3.199 6.137a4.5 4.5 0 0 1-1.646 6.04ZM15.155 4.185a4.47 4.47 0 0 1 2.873 1.021l-.142-.085-4.783-2.758a.771.771 0 0 0-.78 0L6.479 5.731V3.399a.08.08 0 0 1 .033-.061l6.137-3.199a4.5 4.5 0 0 1 6.04 1.646Z"/>
    </svg>
  ),
  GoogleCalendar: () => (
    <svg viewBox="0 0 24 24" className="w-8 h-8 fill-[#4285F4]">
      <path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10z"/>
    </svg>
  ),
  HubSpot: () => (
    <svg viewBox="0 0 24 24" className="w-8 h-8 fill-[#FF7A59]">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3-11h-2v2h-2v2h2v2h2v-2h2v-2h-2z"/>
    </svg>
  ),
  Zapier: () => (
    <svg viewBox="0 0 24 24" className="w-8 h-8 fill-[#FF4A00]">
      <path d="M13.24 2.15l-9.1 11.23h7.24L9.84 21.85l9.53-11.53h-7.66l1.53-8.17z"/>
    </svg>
  )
};

const integrations = [
  { name: "WhatsApp", icon: BrandLogos.WhatsApp, role: "Canal de Atención", position: "-translate-x-[120px] -translate-y-[80px]" },
  { name: "G. Sheets", icon: BrandLogos.GoogleSheets, role: "Base de Datos", position: "translate-x-[120px] -translate-y-[80px]" },
  { name: "Calendario", icon: BrandLogos.GoogleCalendar, role: "Agendamiento", position: "-translate-x-[140px] translate-y-[60px]" },
  { name: "CRM", icon: BrandLogos.HubSpot, role: "Gestión Comercial", position: "translate-x-[140px] translate-y-[60px]" },
  { name: "OpenAI", icon: BrandLogos.OpenAI, role: "Cerebro Lógico", position: "translate-y-[130px]" },
  { name: "Zapier", icon: BrandLogos.Zapier, role: "Automatización", position: "-translate-y-[130px]" },
];

export function IntegrationsSection() {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setIsVisible(true); },
      { threshold: 0.2 }
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section ref={sectionRef} className="py-24 lg:py-32 bg-background overflow-hidden relative">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12 relative z-10">
        
        <div className="text-center max-w-2xl mx-auto mb-20">
          <span className="inline-flex items-center gap-3 text-sm font-mono text-primary font-bold uppercase tracking-widest mb-6">
            Ecosistema
          </span>
          <h2 className={cn("text-3xl lg:text-5xl font-display tracking-tight text-foreground transition-all duration-700", isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4")}>
            Se conecta con las apps que ya sabes usar.
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            No tienes que instalar programas nuevos ni aprender software complejo. Nosotros hacemos que todo tu ecosistema hable entre sí.
          </p>
        </div>

        {/* Visualización tipo "Red de Conexión" */}
        <div className="relative h-[450px] w-full max-w-[800px] mx-auto flex items-center justify-center">
          
          {/* Líneas de conexión animadas de fondo */}
          <div className="absolute inset-0 flex items-center justify-center opacity-30">
            <svg className="w-full h-full" viewBox="0 0 400 400">
              <circle cx="200" cy="200" r="120" stroke="currentColor" className="text-border animate-[spin_20s_linear_infinite]" strokeWidth="1" strokeDasharray="4 4" fill="none" />
              <circle cx="200" cy="200" r="180" stroke="currentColor" className="text-border animate-[spin_30s_linear_infinite_reverse]" strokeWidth="1" strokeDasharray="4 4" fill="none" />
            </svg>
          </div>

          {/* Centro: Logo de ClapWise IA */}
          <div className="absolute z-20 w-24 h-24 bg-foreground rounded-3xl shadow-2xl flex items-center justify-center transform hover:scale-105 transition-transform duration-300">
             <div className="text-center">
                <span className="text-2xl font-display font-bold text-background block leading-none">CW</span>
                <span className="text-[10px] text-background/80 font-mono tracking-widest mt-1 block">IA</span>
             </div>
             {/* Ondas pulsantes centrales */}
             <div className="absolute inset-0 rounded-3xl border border-foreground animate-ping opacity-20" style={{ animationDuration: '3s' }} />
          </div>

          {/* Nodos de Integraciones */}
          {integrations.map((app, index) => {
            const Icon = app.icon;
            return (
              <div 
                key={app.name}
                className={cn(
                  "absolute z-10 transition-all duration-1000",
                  isVisible ? "opacity-100 scale-100" : "opacity-0 scale-50"
                )}
                style={{ transitionDelay: `${index * 150}ms` }}
              >
                <div className={cn("group flex flex-col items-center gap-3", app.position)}>
                  <div className="w-16 h-16 bg-white border border-border shadow-lg rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:-translate-y-1 transition-all duration-300 relative">
                    <Icon />
                    {/* Tooltip on hover */}
                    <div className="absolute -top-10 scale-0 group-hover:scale-100 transition-transform bg-foreground text-background text-xs px-3 py-1 rounded shadow-xl whitespace-nowrap font-medium">
                      {app.role}
                    </div>
                  </div>
                  <span className="text-sm font-medium text-muted-foreground group-hover:text-foreground transition-colors">
                    {app.name}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}