// src/components/BudgetWidget.jsx
import React, { useState } from 'react';

export default function BudgetWidget({ onClose }) {
  const [ingresos, setIngresos] = useState('');
  const [gastos, setGastos] = useState('');
  const [resultado, setResultado] = useState(null);

  const calcular = () => {
    const neto = parseFloat(ingresos) - parseFloat(gastos);
    if (neto > 0) {
      setResultado(`Te sobran $${neto}. Mariana dice: "Nada mal, pero invierte el 20% mínimo."`);
    } else {
      setResultado(`Estás en números rojos ($${neto}). Mariana dice: "Te lo dije. Urge recortar gastos."`);
    }
  };

  return (
    <div className="budget-widget">
      <div className="budget-header">
        <h3>📊 Análisis Financiero (Modo Despacho)</h3>
        <button onClick={onClose} className="close-btn">X</button>
      </div>
      <div className="budget-body">
        <label>Ingresos Mensuales Netos:</label>
        <input type="number" value={ingresos} onChange={(e) => setIngresos(e.target.value)} placeholder="$0.00" />
        
        <label>Gastos Fijos:</label>
        <input type="number" value={gastos} onChange={(e) => setGastos(e.target.value)} placeholder="$0.00" />
        
        <button onClick={calcular} className="calc-btn">Calcular Diagnóstico</button>
        
        {resultado && <div className="budget-result">{resultado}</div>}
      </div>
    </div>
  );
}