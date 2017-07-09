class Attribute:
    def __init__(self, col_name: str) -> None:
        self.col_name = col_name

    def __str__(self) -> str:
        return self.col_name

    def __repr__(self) -> str:
        return f'<plot_config.{type(self).__name__}: {self.col_name}>'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Attribute):
            return NotImplemented
        return type(self).__name__ == type(other).__name__ and self.col_name == other.col_name

    def __hash__(self) -> int:
        return hash(repr(self))


class Dimension(Attribute):
    def __init__(self, col_name: str) -> None:
        super().__init__(col_name)


class Measure(Attribute):
    def __init__(self, col_name: str, *, aggregation: str = 'sum') -> None:
        super().__init__(col_name)
        self.aggregation = aggregation
