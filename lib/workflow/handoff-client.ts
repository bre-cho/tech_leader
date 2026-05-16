"use client";

export type DomainHandoffPayload = {
  source?: string;
  workflowId?: string;
  createdAt?: string;
  request?: {
    storyboard?: Array<Record<string, unknown>>;
    [key: string]: unknown;
  };
  providerPayloadResult?: Record<string, unknown>;
  videoFlowCompile?: Record<string, unknown>;
  [key: string]: unknown;
};

function toJson(value: unknown): string {
  return JSON.stringify(value);
}

export function persistDomainHandoff(sourceKey: string, payload: DomainHandoffPayload): DomainHandoffPayload {
  const normalized: DomainHandoffPayload = {
    createdAt: payload.createdAt ?? new Date().toISOString(),
    ...payload,
    source: sourceKey,
  };

  const json = toJson(normalized);
  sessionStorage.setItem(`handoff:${sourceKey}:latest`, json);
  localStorage.setItem(`handoff:${sourceKey}:latest`, json);
  localStorage.setItem("handoff:global:latest", json);

  return normalized;
}
