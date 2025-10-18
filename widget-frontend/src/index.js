// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import MantineApp from './App'; // импортируем наш новый компонент

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <MantineApp />
  </React.StrictMode>
);