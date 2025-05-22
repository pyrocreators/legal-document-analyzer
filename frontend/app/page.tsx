"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useRef, useState } from "react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");
  const [endpoint, setEndpoint] = useState<"summary" | "key-points">("summary");

  const [legalQuestion, setLegalQuestion] = useState("");
  const [legalResponse, setLegalResponse] = useState("");
  const [legalLoading, setLegalLoading] = useState(false);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setResult("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`http://localhost:8000/${endpoint}/`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload file");
      }

      const data = await response.json();
      setResult(data.summary);
    } catch (error) {
      setResult("Something went wrong. Please try again.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleLegalQuery = async () => {
    if (!legalQuestion) return;

    setLegalLoading(true);
    setLegalResponse("");

    try {
      const response = await fetch(
        `http://localhost:8000/legal-terminology/?question=${encodeURIComponent(
          legalQuestion
        )}`
      );
      if (!response.ok) throw new Error("Request failed");
      const data = await response.json();
      setLegalResponse(data.response);
    } catch (error) {
      setLegalResponse("Error fetching legal information.");
      console.error(error);
    } finally {
      setLegalLoading(false);
    }
  };

  function formatMarkdownToHTML(text: string): string {
    return text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/^- (.*)/gm, "<p>$1</p>");
  }

  function formatWikipediaResponse(text: string): string {
    return (
      text
        // remove special HTML characters
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")

        // make **bold**
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")

        // number points into subheadings
        .replace(
          /^(\d+)\.\s(.+?)$/gm,
          "<h4 class='mt-4 mb-1 font-semibold'>$1. $2</h4>"
        )

        // markdown-style links
        .replace(
          /\[([^\]]+)\]\(([^)]+)\)/g,
          `<a href="$2" class="text-blue-600 underline" target="_blank" rel="noopener noreferrer">$1</a>`
        )

        // add paragraph tags and preserve paragraphs
        .split(/\n{2,}/g)
        .map((paragraph) => `<p class="mb-2">${paragraph.trim()}</p>`)
        .join("")
    );
  }

  return (
    <main className="max-w-xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Legal Document Analyzer</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
          />
          <Tabs
            defaultValue="summary"
            onValueChange={(val) => {
              setEndpoint(val as "summary" | "key-points");
              setResult("");
              setFile(null);
              if (fileInputRef.current) {
                fileInputRef.current.value = "";
              }
            }}
          >
            <TabsList>
              <TabsTrigger value="summary">Summary</TabsTrigger>
              <TabsTrigger value="key-points">Key Points</TabsTrigger>
            </TabsList>
          </Tabs>
          <Button onClick={handleUpload} disabled={loading || !file}>
            {loading ? "Processing..." : "Analyze PDF"}
          </Button>
          <div
            className="p-4 border rounded bg-gray-50 space-y-2 text-sm"
            dangerouslySetInnerHTML={{ __html: formatMarkdownToHTML(result) }}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Legal Terminology Searcher</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            placeholder="Enter a legal question or term..."
            value={legalQuestion}
            onChange={(e) => setLegalQuestion(e.target.value)}
          />
          <Button
            onClick={handleLegalQuery}
            disabled={legalLoading || !legalQuestion}
          >
            {legalLoading ? "Searching..." : "Search Legal Terminology"}
          </Button>
          {legalResponse && (
            <div
              className="p-4 border rounded bg-gray-50 space-y-2 text-sm"
              dangerouslySetInnerHTML={{
                __html: formatWikipediaResponse(legalResponse),
              }}
            />
          )}
        </CardContent>
      </Card>
    </main>
  );
}
