"use client";

import { ArrowUpRight, TerminalSquare } from "lucide-react";
import { AnimatedWave } from "./animated-wave";

const footerLinks = {
  Sectores: [
    { name: "E-commerce y Tiendas Online", href: "#" },
    { name: "Negocios Locales y Franquicias", href: "#" },
    { name: "Retail e Inventarios", href: "#" },
  ],
  Agencia: [
    { name: "Nuestra Metodología (NDA)", href: "#" },
    { name: "Auditoría Gratuita", href: "#", badge: "Destacado" },
    { name: "Panel de Looker Studio", href: "#" },
  ],
  Legal: [
    { name: "Acuerdos de Privacidad", href: "#" },
    { name: "Protección de Datos", href: "#" },
  ],
};

const socialLinks = [
  { name: "LinkedIn", href: "#" },
  { name: "GitHub", href: "#" },
];

export function FooterSection() {
  return (
    <footer className="relative border-t border-border bg-background">
      <div className="absolute inset-0 h-64 opacity-10 pointer-events-none overflow-hidden">
        <AnimatedWave />
      </div>
      
      <div className="relative z-10 max-w-[1400px] mx-auto px-6 lg:px-12">
        <div className="py-16 lg:py-24">
          <div className="grid grid-cols-1 md:grid-cols-6 gap-12 lg:gap-8">
            
            <div className="col-span-1 md:col-span-2">
              <a href="#" className="inline-flex items-center gap-2 mb-6">
                <span className="text-2xl font-display font-bold text-foreground">Clapwise</span>
                <span className="text-xs text-primary font-mono flex items-center gap-1">
                  <TerminalSquare className="w-3 h-3" />
                  MATH
                </span>
              </a>

              <p className="text-muted-foreground leading-relaxed mb-8 max-w-sm">
                Transformamos historiales de ventas en espacios vectoriales. Optimizamos márgenes comerciales a través de programación lineal e inteligencia de datos.
              </p>

              <div className="flex gap-6">
                {socialLinks.map((link) => (
                  <a
                    key={link.name}
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-primary transition-colors flex items-center gap-1 group"
                  >
                    {link.name}
                    <ArrowUpRight className="w-3 h-3 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                  </a>
                ))}
              </div>
            </div>

            {Object.entries(footerLinks).map(([title, links]) => (
              <div key={title} className="col-span-1">
                <h3 className="text-sm font-semibold text-foreground mb-6 uppercase tracking-wider">{title}</h3>
                <ul className="space-y-4">
                  {links.map((link) => (
                    <li key={link.name}>
                      <a
                        href={link.href}
                        className="text-sm text-muted-foreground hover:text-primary transition-colors inline-flex items-center gap-2"
                      >
                        {link.name}
                        {"badge" in link && link.badge && (
                          <span className="text-[10px] px-2 py-0.5 bg-primary/10 text-primary border border-primary/20 rounded-full font-mono">
                            {link.badge}
                          </span>
                        )}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="py-8 border-t border-border flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} Clapwise Analytics. Todos los derechos reservados.
          </p>

          <div className="flex items-center gap-4 text-sm font-mono text-muted-foreground">
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              Infraestructura Operativa
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}