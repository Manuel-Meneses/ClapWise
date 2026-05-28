"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Menu, X, TerminalSquare } from "lucide-react";

const navLinks = [
  { name: "Modelado", href: "#features" },
  { name: "Metodología", href: "#how-it-works" },
  { name: "Métricas", href: "#metrics" },
  { name: "Inversión", href: "#pricing" },
];

export function Navigation() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
   <header className={`fixed z-50 transition-all duration-500 ${isScrolled ? "top-4 left-4 right-4" : "top-0 left-0 right-0"}`}>
      <nav className={`mx-auto transition-all duration-500 ${isScrolled || isMobileMenuOpen ? "bg-background/80 backdrop-blur-xl border border-border rounded-2xl shadow-lg max-w-[1200px]" : "bg-transparent max-w-[1400px]"}`}>
        <div className={`flex items-center justify-between transition-all duration-500 px-6 lg:px-8 ${isScrolled ? "h-14" : "h-20"}`}>
          
          {/* Logo ClapWise */}
          <a href="#" className="flex items-center gap-2 group">
            <span className={`font-display font-bold tracking-tight text-foreground transition-all duration-500 ${isScrolled ? "text-xl" : "text-2xl"}`}>Clapwise</span>
            <span className={`text-primary font-mono transition-all duration-500 flex items-center gap-1 ${isScrolled ? "text-[10px]" : "text-xs mt-1"}`}>
              <TerminalSquare className={isScrolled ? "w-3 h-3" : "w-4 h-4"} />
              MATH
            </span>
          </a>

          {/* Enlaces Desktop */}
          <div className="hidden md:flex items-center gap-12">
            {navLinks.map((link) => (
              <a key={link.name} href={link.href} className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors duration-300 relative group">
                {link.name}
                <span className="absolute -bottom-1 left-0 w-0 h-px bg-primary transition-all duration-300 group-hover:w-full" />
              </a>
            ))}
          </div>

          {/* Botones Desktop */}
          <div className="hidden md:flex items-center gap-4">
            <a href="#" className={`font-medium text-muted-foreground hover:text-primary transition-all duration-500 ${isScrolled ? "text-xs" : "text-sm"}`}>
              Portal Cliente
            </a>
            <Button size="sm" className={`bg-primary hover:bg-primary/90 text-white rounded-full transition-all shadow-md shadow-primary/20 duration-500 ${isScrolled ? "px-4 h-8 text-xs" : "px-6"}`}>
              Auditoría Gratuita
            </Button>
          </div> 

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 text-foreground"
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </nav>
      
      {/* Mobile Menu - Full Screen Overlay */}
      <div
        className={`md:hidden fixed inset-0 bg-background z-40 transition-all duration-500 ${
          isMobileMenuOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        }`}
        style={{ top: 0 }}
      >
        <div className="flex flex-col h-full px-8 pt-28 pb-8">
          <div className="flex-1 flex flex-col justify-center gap-8">
            {navLinks.map((link, i) => (
              <a
                key={link.name}
                href={link.href}
                onClick={() => setIsMobileMenuOpen(false)}
                className={`text-5xl font-display text-foreground hover:text-primary transition-all duration-500 ${
                  isMobileMenuOpen ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
                }`}
                style={{ transitionDelay: isMobileMenuOpen ? `${i * 75}ms` : "0ms" }}
              >
                {link.name}
              </a>
            ))}
          </div>
          
          <div className={`flex flex-col gap-4 pt-8 border-t border-border transition-all duration-500 ${
            isMobileMenuOpen ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
          style={{ transitionDelay: isMobileMenuOpen ? "300ms" : "0ms" }}
          >
            <Button variant="outline" className="w-full rounded-full h-14 text-base" onClick={() => setIsMobileMenuOpen(false)}>
              Portal de Clientes
            </Button>
            <Button className="w-full bg-primary text-white hover:bg-primary/90 rounded-full h-14 text-base shadow-lg shadow-primary/20" onClick={() => setIsMobileMenuOpen(false)}>
              Solicitar Auditoría Gratis
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}