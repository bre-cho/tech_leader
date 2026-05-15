"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { PipelineShell } from "@/components/layout/PipelineShell";
import { RuntimePanel } from "@/components/runtime/RuntimePanel";
import { ProjectWorkspace } from "@/components/workflow/ProjectWorkspace";
import { WorkflowSidebar } from "@/components/workflow/WorkflowSidebar";
import { buildV31RequestFromPipeline } from "@/lib/design/pipeline-handoff";
import {
  defaultDesignBrief,
  runDesignStudio,
  type DesignStudioRequest,
  type DesignStudioResponse,
} from "@/lib/design/pipeline-api";

export default function ProjectPipelinePage() {
  const router = useRouter();
  const [brief, setBrief] = useState<DesignStudioRequest>(defaultDesignBrief);
  const [result, setResult] = useState<DesignStudioResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [handoffLoading, setHandoffLoading] = useState(false);
  const [handoffError, setHandoffError] = useState<string | null>(null);
  const [handoffStatus, setHandoffStatus] = useState<string | null>(null);

  const updateBrief = <K extends keyof DesignStudioRequest>(field: K, value: DesignStudioRequest[K]) => {
    setBrief((current) => ({ ...current, [field]: value }));
  };

  const runHandoffAndCompile = async (pipelineResult: DesignStudioResponse) => {
    setHandoffLoading(true);
    setHandoffError(null);
    setHandoffStatus("handoff-running");
    try {
      const v31Request = buildV31RequestFromPipeline(brief, pipelineResult);
      const handoffResponse = await fetch("/api/storyboard/v31/provider-payloads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(v31Request),
      });

      if (!handoffResponse.ok) {
        const message = await handoffResponse.text();
        throw new Error(message || "V31 handoff failed.");
      }

      const handoffResult = (await handoffResponse.json()) as { status?: string };

      const compileResponse = await fetch("/api/videoflow/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(v31Request),
      });

      if (!compileResponse.ok) {
        const message = await compileResponse.text();
        throw new Error(message || "VideoFlow compile failed.");
      }

      const compileResult = (await compileResponse.json()) as {
        status?: string;
        videoFlowTimeline?: unknown;
      };

      setHandoffStatus(`handoff:${handoffResult.status || "ready"} / compile:${compileResult.status || "ready"}`);

      sessionStorage.setItem(
        "pipeline-os:v31-handoff",
        JSON.stringify({
          source: "pipeline-os",
          request: v31Request,
          providerPayloadResult: handoffResult,
          videoFlowCompile: compileResult,
          workflowId: pipelineResult.workflow_id,
          createdAt: new Date().toISOString(),
        }),
      );

      router.push("/storyboard-v31?source=pipeline-os&autorun=1");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "V31 handoff failed.";
      setHandoffError(message);
    } finally {
      setHandoffLoading(false);
    }
  };

  const handleRun = async () => {
    setIsRunning(true);
    setError(null);
    setHandoffError(null);
    setHandoffStatus(null);
    try {
      const response = await runDesignStudio(brief);
      setResult(response);
      await runHandoffAndCompile(response);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Khong the goi Design Studio API.";
      setError(message);
    } finally {
      setIsRunning(false);
    }
  };

  const handleOpenVideoStudio = async () => {
    if (!result) {
      setHandoffError("Can run pipeline before handoff.");
      return;
    }
    await runHandoffAndCompile(result);
  };

  return (
    <div>
      <PipelineShell>
        <WorkflowSidebar isRunning={isRunning} result={result} />
        <ProjectWorkspace
          brief={brief}
          error={error}
          handoffError={handoffError}
          handoffLoading={handoffLoading}
          handoffStatus={handoffStatus}
          isRunning={isRunning}
          onOpenVideoStudio={handleOpenVideoStudio}
          onRun={handleRun}
          onUpdateBrief={updateBrief}
          result={result}
        />
        <RuntimePanel error={error} isRunning={isRunning} result={result} />
      </PipelineShell>
    </div>
  );
}
