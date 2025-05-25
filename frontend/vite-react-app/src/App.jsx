import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import './App.css'; // Keep if it contains any global styles you want, or remove if not needed.

function App() {
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4 space-y-8">
      <div className="flex space-x-4">
        <Button className="bg-softYellow text-softYellow-foreground hover:bg-softYellow/90">
          Soft Yellow Button
        </Button>
        <Button className="bg-softOrange text-softOrange-foreground hover:bg-softOrange/90">
          Soft Orange Button
        </Button>
      </div>

      <Card className="w-full max-w-md">
        <CardHeader className="bg-primary/10"> {/* Using a very light shade of the primary yellow from the theme */}
          <CardTitle>Themed Card Title</CardTitle>
        </CardHeader>
        <CardContent>
          <CardDescription className="mt-2">
            This card demonstrates the use of shadcn/ui components
            with a custom soft yellow/orange theme influence. The header
            has a light primary background.
          </CardDescription>
        </CardContent>
        <CardFooter>
          <p>Card Footer Content</p>
        </CardFooter>
      </Card>
    </div>
  );
}

export default App;
