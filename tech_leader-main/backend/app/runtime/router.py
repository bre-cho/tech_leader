class CapabilityRouter:
    def route(self, plan):
        return [
            {"capability": "business_diagnosis", "agent": "BusinessDiagnosisAgent"},
            {"capability": "image_design", "agent": "ImageDesignAgent"},
            {"capability": "image_scoring", "agent": "ImageQAAgent"},
            {"capability": "upsell_analysis", "agent": "UpsellOpportunityAgent"},
            {"capability": "video_concept_preview", "agent": "VideoConceptAgent"},
            {"capability": "storyboard", "agent": "StoryboardAgent"},
            {"capability": "offer_packaging", "agent": "OfferAgent"},
        ]
