import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function StatsSection() {
  return (
    <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Open Scholarships
          </CardTitle>
        </CardHeader>

        <CardContent>
          <p className="text-2xl font-semibold">12</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            New Scholarships
          </CardTitle>
        </CardHeader>

        <CardContent>
          <p className="text-2xl font-semibold">3</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Sources
          </CardTitle>
        </CardHeader>

        <CardContent>
          <p className="text-2xl font-semibold">1</p>
        </CardContent>
      </Card>
    </section>
  );
}