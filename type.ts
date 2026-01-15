type CommandArgument =
    | string
    | {
        flag: "if_set";
        variable: string;
        values: string[];
    };


export interface MCPServiceConfig {
    id: string;
    name: string;
    description: string;
    author: string;
    icon: string;
    version: string;
    modes: ServiceMode[];
}

export interface ServiceMode {
    type: "stdio" | "sse";
    runner: "npx" | "docker" | "python" | "binary";
    isDefault?: boolean;
    prerequisites?: string[];
    inputs: ConfigInput[];
    commandTemplate: {
        command: string;
        args: CommandArgument[];
        env?: Record<string, string>;
    };
}

export interface ConfigInput {
    id: string;
    label: string;
    type: "text" | "password" | "path" | "select";
    description?: string;
    placeholder?: string;
    defaultValue?: string;
    required: boolean;
}