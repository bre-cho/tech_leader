import React from 'react';
import { createRoot } from 'react-dom/client';
import DesignStudio from './pages/DesignStudio';
import DesignStudioCreativeOS from './pages/DesignStudioCreativeOS';
import DesignStudioCreativeOSV2 from './pages/DesignStudioCreativeOSV2';
import FashionMovieStudio from './pages/FashionMovieStudio';
import './styles.css';

const search = new URLSearchParams(window.location.search);
const hasHandoffMarker = search.has('handoff');
const hasFashionHandoff = search.has('fashion_handoff');
const hasNamedPayload = typeof window.name === 'string' && window.name.trim().length > 0;
let effectivePath = window.location.pathname;

function parseEncodedHandoff(value: string | null): Record<string, unknown> | null {
	if (!value) return null;
	try {
		return JSON.parse(decodeURIComponent(value)) as Record<string, unknown>;
	} catch {
		return null;
	}
}

const handoffPayload = parseEncodedHandoff(search.get('handoff'));
const isV2Handoff = Boolean(
	handoffPayload &&
		typeof handoffPayload.current_render_index === 'number' &&
		handoffPayload.execution_mode === 'sequential'
);

if ((hasHandoffMarker || hasNamedPayload) && effectivePath !== (isV2Handoff ? '/creative-os-v2' : '/creative-os')) {
	const next = new URL(window.location.href);
	next.pathname = isV2Handoff ? '/creative-os-v2' : '/creative-os';
	if (hasHandoffMarker && !next.searchParams.has('handoff')) {
		next.searchParams.set('handoff', '1');
	}
	window.history.replaceState(null, '', `${next.pathname}${next.search}${next.hash}`);
	effectivePath = next.pathname;
}

const isCreativePath = effectivePath === '/creative-os';
const isCreativePathV2 = effectivePath === '/creative-os-v2';
const hasCreativeHandoff = isCreativePath || hasHandoffMarker || hasNamedPayload;
const hasCreativeHandoffV2 = isCreativePathV2 || isV2Handoff;

createRoot(document.getElementById('root')!).render(
	hasFashionHandoff ? <FashionMovieStudio /> : hasCreativeHandoffV2 ? <DesignStudioCreativeOSV2 /> : hasCreativeHandoff ? <DesignStudioCreativeOS /> : <DesignStudio />
);
