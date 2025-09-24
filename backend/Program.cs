var builder = WebApplication.CreateBuilder(args);

// Register services
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Enable Swagger in dev only
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// Middlewares
app.UseHttpsRedirection();
app.MapControllers(); // for attribute-routed controllers

// Minimal API routes
app.MapGet("/", () => Results.Redirect("/swagger"));
app.MapGet("/health", () => "OK");
app.MapGet("/hello", () => "Hello World!");

app.Run();
