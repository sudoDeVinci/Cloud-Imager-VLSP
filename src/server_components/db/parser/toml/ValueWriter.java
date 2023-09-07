package server_components.db.parser.toml;

interface ValueWriter {
  boolean canWrite(Object value);

  void write(Object value, WriterContext context);

  boolean isPrimitiveType();
}
