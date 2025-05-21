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

  function formatMarkdownToHTML(text: string): string {
    return text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/^- (.*)/gm, "<p>$1</p>");
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
      </main>
  );
}

