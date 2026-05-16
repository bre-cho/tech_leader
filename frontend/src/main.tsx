import React from 'react';
import { createRoot } from 'react-dom/client';
import DesignStudio from './pages/DesignStudio';
import DesignStudioCreativeOS from './pages/DesignStudioCreativeOS';
import './styles.css';

const search = new URLSearchParams(window.location.search);
const hasHandoffMarker = search.has('handoff');
const hasNamedPayload = typeof window.name === 'string' && window.name.trim().length > 0;
let effectivePath = window.location.pathname;

if ((hasHandoffMarker || hasNamedPayload) && effectivePath !== '/creative-os') {
	const next = new URL(window.location.href);
	next.pathname = '/creative-os';
	if (hasHandoffMarker && !next.searchParams.has('handoff')) {
		next.searchParams.set('handoff', '1');
	}
	window.history.replaceState(null, '', `${next.pathname}${next.search}${next.hash}`);
	effectivePath = '/creative-os';
}

const isCreativePath = effectivePath === '/creative-os';
const hasCreativeHandoff = isCreativePath || hasHandoffMarker || hasNamedPayload;

createRoot(document.getElementById('root')!).render(
	hasCreativeHandoff ? <DesignStudioCreativeOS /> : <DesignStudio />
);
