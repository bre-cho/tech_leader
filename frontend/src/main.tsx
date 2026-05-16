import React from 'react';
import { createRoot } from 'react-dom/client';
import DesignStudio from './pages/DesignStudio';
import DesignStudioCreativeOS from './pages/DesignStudioCreativeOS';
import './styles.css';

const search = new URLSearchParams(window.location.search);
const hasCreativeHandoff = search.has('handoff');

createRoot(document.getElementById('root')!).render(
	hasCreativeHandoff ? <DesignStudioCreativeOS /> : <DesignStudio />
);
