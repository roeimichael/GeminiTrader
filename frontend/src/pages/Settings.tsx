import { AppLayout } from '@/components/AppLayout';
import { useSessionStore } from '@/store/sessionStore';
import { useDeleteSession, useHealth } from '@/hooks/useApi';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import { Trash2, Server, Clock, Users } from 'lucide-react';

const Settings = () => {
  const { sessionId, reset } = useSessionStore();
  const { mutate: deleteSession, isPending: isDeleting } = useDeleteSession();
  const { data: health } = useHealth();

  const handleDeleteSession = () => {
    if (sessionId) {
      deleteSession(sessionId);
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6 max-w-2xl">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            Manage your session and application settings
          </p>
        </div>

        {/* API Status */}
        <Card className="gradient-card border-border/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="w-5 h-5" />
              API Status
            </CardTitle>
            <CardDescription>
              Connection status to the GeminiTrader backend
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label className="text-muted-foreground text-xs">Status</Label>
                <div className="flex items-center gap-2">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      health?.status === 'healthy' ? 'bg-bullish' : 'bg-bearish'
                    }`}
                  />
                  <span className="font-medium capitalize">
                    {health?.status || 'Unknown'}
                  </span>
                </div>
              </div>
              <div className="space-y-1">
                <Label className="text-muted-foreground text-xs">Version</Label>
                <span className="font-mono">{health?.version || 'N/A'}</span>
              </div>
              <div className="space-y-1">
                <Label className="text-muted-foreground text-xs">Active Sessions</Label>
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-muted-foreground" />
                  <span>{health?.active_sessions ?? 'N/A'}</span>
                </div>
              </div>
              <div className="space-y-1">
                <Label className="text-muted-foreground text-xs">Last Check</Label>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm">
                    {health?.timestamp
                      ? new Date(health.timestamp).toLocaleTimeString()
                      : 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Session Management */}
        <Card className="gradient-card border-border/50">
          <CardHeader>
            <CardTitle>Session Management</CardTitle>
            <CardDescription>
              Manage your current analysis session
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="session-id">Current Session ID</Label>
              <Input
                id="session-id"
                value={sessionId || 'No active session'}
                readOnly
                className="font-mono"
              />
            </div>

            <Separator />

            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => reset()}
                className="flex-1"
              >
                Reset Local State
              </Button>
              <Button
                variant="destructive"
                onClick={handleDeleteSession}
                disabled={!sessionId || isDeleting}
                className="flex-1 gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Delete Session
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* API Configuration */}
        <Card className="gradient-card border-border/50">
          <CardHeader>
            <CardTitle>API Configuration</CardTitle>
            <CardDescription>
              Backend API endpoint settings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="api-url">API Base URL</Label>
              <Input
                id="api-url"
                value="http://localhost:8000"
                readOnly
                className="font-mono"
              />
              <p className="text-xs text-muted-foreground">
                Configure in src/lib/api.ts to change the endpoint
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
};

export default Settings;
