import Navbar from "@/components/layout/Navbar";
import SearchSection from "@/components/layout/SearchSection";
import StatsSection from "@/components/layout/StatsSection";
import ContentSection from "@/components/layout/ContentSection";

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 p-4 sm:p-6">
        <Navbar />
        <SearchSection />
        <StatsSection />
        <ContentSection />
      </div>
    </main>
  );
}