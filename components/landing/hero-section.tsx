"use client";

import { useEffect, useState, memo } from "react";
import { Button } from "@/components/ui/button";
import { ArrowRight, ShieldCheck, Activity, Cpu } from "lucide-react";

// Reducimos la matriz a 7x7 (49 nodos) para aliviar el DOM en Chrome sin perder impacto visual
const generateRandomData = () => Array.from({ length: 49 }, () => Math.floor(Math.random() * 99));

// Memoizamos las celdas para que React no re-renderice las que no cambian
const GridCell = memo(({ num, isOptimizing, isOptimalPath, isVertex }: any) => {
  return (
    <div 
      className={`w-10 h-10 flex justify-center items-center rounded-lg font-mono text-xs transition-all duration-500 hardware-accelerated ${
        isOptimizing 
          ? isVertex 
            ? "bg-emerald-500 text-white shadow-[0_10px_30px_rgba(16,185,129,0.5)] scale-125 z-20 font-bold border-2 border-emerald-400"
            : isOptimalPath
              ? "bg-emerald-100 text-emerald-700 border border-emerald-300 scale-110 z-10 font-bold"
              : "bg-transparent text-slate-300 scale-95 opacity-40"
          : "bg-slate-50 text-slate-400 border border-slate-200"
      }`}
    >
      {isOptimizing && isVertex ? "MAX" : num.toString().padStart(2, '0')}
    </div>
  );
});
GridCell.displayName = "GridCell";

export function HeroSection() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [dataGrid, setDataGrid] = useState<number[]>(generateRandomData());
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [profitMargin, setProfitMargin] = useState(0);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  // Simulación optimizada para Chrome (Menos re-renders por segundo)
  useEffect(() => {
    const chaosInterval = setInterval(() => {
      if (!isOptimizing) {
        // En lugar de cambiar todos los números, cambiamos solo un 30% de ellos en cada ciclo
        setDataGrid(prev => prev.map(val => Math.random() > 0.7 ? Math.floor(Math.random() * 99) : val));
      }
    }, 400); // 400ms le da a Chrome espacio para respirar

    const optimizationCycle = setInterval(() => {
      setIsOptimizing(true);
      setTimeout(() => {
        setProfitMargin((prev) => +(prev + 2.4).toFixed(1));
        setIsOptimizing(false);
      }, 2500); 
    }, 6000); // Ciclo más largo para apreciar el resultado

    return () => {
      clearInterval(chaosInterval);
      clearInterval(optimizationCycle);
    };
  }, [isOptimizing]);

  return (
    <section className="relative min-h-screen flex flex-col justify-center overflow-hidden bg-white pt-32 pb-20">
      
      {/* Luces Ambientales (Claras y Limpias) */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-emerald-100 blur-[120px] opacity-70 mix-blend-multiply" />
        <div className="absolute top-[40%] -right-[10%] w-[40%] h-[60%] rounded-full bg-blue-50 blur-[120px] mix-blend-multiply" />
      </div>
      
      {/* Patrón de puntos sutil para fondo blanco */}
      <div className="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:24px_24px] opacity-60 pointer-events-none" />
      
      <div className="relative z-10 max-w-[1400px] mx-auto px-6 lg:px-12 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-24 items-center">
          
          {/* Columna Izquierda: Copywriting Institucional */}
          <div className="flex flex-col relative z-20">
            <div 
              className={`mb-8 inline-flex items-center gap-2 px-4 py-2 rounded-full border border-emerald-200 bg-emerald-50 w-fit transition-all duration-1000 delay-100 ${
                isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
              }`}
            >
              <Cpu className="w-4 h-4 text-emerald-600" />
              <span className="text-xs font-mono font-bold tracking-widest text-emerald-700 uppercase">
                Arquitectura de Datos Financiera
              </span>
            </div>
            
            <div className="mb-6">
              <h1 
                className={`text-[clamp(2.5rem,5.5vw,5rem)] font-display leading-[1.05] tracking-tight text-slate-900 transition-all duration-1000 delay-200 ${
                  isLoaded ? "opacity-100 translate-y-0 blur-none" : "opacity-0 translate-y-8 blur-sm"
                }`}
              >
                Transformamos la <span className="italic text-slate-400 font-light">entropía</span> en <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-500">rentabilidad pura.</span>
              </h1>
            </div>
            
            <div 
              className={`transition-all duration-1000 delay-300 ${
                isLoaded ? "opacity-100 translate-y-0 blur-none" : "opacity-0 translate-y-4 blur-sm"
              }`}
            >
              <p className="text-lg md:text-xl text-slate-600 leading-relaxed max-w-xl mb-10 font-light">
                No hacemos marketing. Construimos modelos de álgebra lineal sobre tu historial de ventas para erradicar el stock muerto y predecir la demanda exacta. <strong className="text-slate-900 font-semibold">Precisión matemática para tu negocio.</strong>
              </p>
              
              <div className="flex flex-col sm:flex-row items-center gap-5">
                <Button 
                  size="lg" 
                  className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold border-0 shadow-[0_12px_30px_-10px_rgba(16,185,129,0.4)] px-8 h-14 text-base rounded-full group w-full sm:w-auto transition-all"
                >
                  Solicitar Diagnóstico Gratis
                  <ArrowRight className="w-4 h-4 ml-2 transition-transform group-hover:translate-x-1" />
                </Button>
              </div>

              <div className="mt-8 flex items-center gap-3 text-xs text-slate-500 font-mono">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span>NDA Activo. Sin acceso a cuentas bancarias ni claves.</span>
              </div>
            </div>
          </div>

          {/* Columna Derecha: Matriz Isométrica 3D (Optimizada para GPU) */}
          <div 
            className={`relative flex justify-center items-center h-[500px] transition-all duration-1000 delay-500 ${
              isLoaded ? "opacity-100 translate-x-0" : "opacity-0 translate-x-12"
            }`}
          >
            <div className="isometric-container w-full h-full flex justify-center items-center">
              
              {/* Cuadrícula de Datos (Matriz 7x7) */}
              <div className={`data-grid grid grid-cols-7 gap-3 p-8 rounded-3xl border border-slate-200 bg-white shadow-[0_20px_60px_-15px_rgba(0,0,0,0.05)] transition-all duration-700 ${isOptimizing ? "optimizing shadow-[0_30px_80px_-20px_rgba(16,185,129,0.2)] border-emerald-200" : ""}`}>
                
                <div className="scanner-beam" />

                {dataGrid.map((num, i) => {
                  // Ruta óptima en grilla de 7x7
                  const isOptimalPath = [0, 8, 16, 24, 25, 26, 19, 12].includes(i);
                  const isVertex = i === 12; 

                  return (
                    <GridCell 
                      key={i} 
                      num={num} 
                      isOptimizing={isOptimizing} 
                      isOptimalPath={isOptimalPath} 
                      isVertex={isVertex} 
                    />
                  );
                })}
              </div>

              {/* Insignias Flotantes 3D (Tema Claro) */}
              <div className="absolute -right-4 lg:-right-12 top-1/4 floating-badge delay-100 z-30">
                <div className="px-5 py-3 rounded-xl bg-white/90 border border-slate-200 backdrop-blur-xl flex items-center gap-4 shadow-xl">
                  <Activity className="w-5 h-5 text-slate-700" />
                  <div className="flex flex-col">
                    <span className="text-[10px] text-slate-500 font-mono uppercase tracking-wider">Varianza Reducida</span>
                    <span className="text-sm font-mono text-slate-900 font-bold">σ² ≈ 0.024</span>
                  </div>
                </div>
              </div>

              <div className="absolute -left-4 lg:-left-12 bottom-1/4 floating-badge delay-300 z-30">
                <div className="px-5 py-3 rounded-xl bg-emerald-50 border border-emerald-100 backdrop-blur-xl flex items-center gap-4 shadow-[0_15px_35px_-10px_rgba(16,185,129,0.2)]">
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                  <div className="flex flex-col">
                    <span className="text-[10px] text-emerald-700 font-mono uppercase tracking-wider">Delta de Ganancia</span>
                    <span className="text-xl font-display text-emerald-600 font-bold">+{profitMargin}%</span>
                  </div>
                </div>
              </div>

            </div>
          </div>

        </div>
      </div>

      {/* CSS con aceleración de Hardware (GPU) */}
      <style jsx>{`
        .isometric-container {
          perspective: 1200px;
          transform-style: preserve-3d;
          will-change: transform;
        }

        .data-grid {
          transform: rotateX(55deg) rotateZ(-45deg);
          transform-style: preserve-3d;
          will-change: transform, box-shadow;
          backface-visibility: hidden;
        }

        .data-grid.optimizing {
          transform: rotateX(55deg) rotateZ(-45deg) translateZ(30px);
        }

        .hardware-accelerated {
          transform: translateZ(0);
          will-change: transform, background-color, color, opacity;
          backface-visibility: hidden;
        }

        .scanner-beam {
          position: absolute;
          top: 0;
          left: -50%;
          width: 200%;
          height: 20px;
          background: linear-gradient(to bottom, transparent, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.4), transparent);
          transform: translateY(-100%) rotateZ(45deg);
          animation: scan 6s cubic-bezier(0.4, 0, 0.2, 1) infinite;
          z-index: 50;
          pointer-events: none;
          will-change: transform, opacity;
        }

        @keyframes scan {
          0% { transform: translateY(-50px) rotateZ(0deg); opacity: 0; }
          10% { opacity: 1; }
          40% { transform: translateY(400px) rotateZ(0deg); }
          50% { opacity: 0; }
          100% { transform: translateY(450px) rotateZ(0deg); opacity: 0; }
        }

        @keyframes float3d {
          0% { transform: translateY(0px) translateZ(40px); }
          50% { transform: translateY(-12px) translateZ(40px); }
          100% { transform: translateY(0px) translateZ(40px); }
        }

        .floating-badge {
          animation: float3d 6s ease-in-out infinite;
          transform-style: preserve-3d;
          will-change: transform;
          backface-visibility: hidden;
        }
        
        .delay-100 { animation-delay: 0.5s; }
        .delay-300 { animation-delay: 2s; }
      `}</style>
    </section>
  );
}