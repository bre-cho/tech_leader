import { Suspense } from "react";
import StoryboardV31RhythmStudio from "@/components/storyboard-v31/StoryboardV31RhythmStudio";

export default function Page() {
  return (
    <Suspense fallback={<main className="min-h-screen bg-neutral-950 p-8 text-white">Loading V31 Studio...</main>}>
      <StoryboardV31RhythmStudio />
    </Suspense>
  );
}
