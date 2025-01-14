from typing import List

import pytest

from odata_query import ast, sql


@pytest.mark.parametrize(
    "ast_input, sql_expected",
    [
        (ast.Compare(ast.Eq(), ast.Integer("1"), ast.Integer("1")), "1 = 1"),
        (
            ast.Compare(ast.NotEq(), ast.Boolean("true"), ast.Boolean("false")),
            "1 != 0",
        ),
        (
            ast.Compare(ast.LtE(), ast.Identifier("eac"), ast.Float("123.12")),
            '"eac" <= 123.12',
        ),
        (
            ast.Compare(
                ast.Lt(),
                ast.Identifier("period_start"),
                ast.Date("2019-01-01"),
            ),
            "\"period_start\" < date('2019-01-01')",
        ),
        (
            ast.BoolOp(
                ast.And(),
                ast.Compare(ast.GtE(), ast.Identifier("eac"), ast.Float("123.12")),
                ast.Compare(
                    ast.In(),
                    ast.Identifier("meter_id"),
                    ast.List([ast.String("1"), ast.String("2"), ast.String("3")]),
                ),
            ),
            "\"eac\" >= 123.12 AND \"meter_id\" IN ('1', '2', '3')",
        ),
        (
            ast.BoolOp(
                ast.And(),
                ast.Compare(ast.Eq(), ast.Identifier("a"), ast.String("1")),
                ast.BoolOp(
                    ast.Or(),
                    ast.Compare(ast.LtE(), ast.Identifier("eac"), ast.Float("10.0")),
                    ast.Compare(ast.GtE(), ast.Identifier("eac"), ast.Float("1.0")),
                ),
            ),
            '"a" = \'1\' AND ("eac" <= 10.0 OR "eac" >= 1.0)',
        ),
    ],
)
def test_ast_to_sql(ast_input: ast._Node, sql_expected: str):
    visitor = sql.AstToSqliteSqlVisitor()
    res = visitor.visit(ast_input)

    assert res == sql_expected


@pytest.mark.parametrize(
    "func_name, args, sql_expected",
    [
        ("concat", [ast.String("ab"), ast.String("cd")], "'ab' || 'cd'"),
        (
            "concat",
            [
                ast.String("a"),
                ast.String("b"),
                ast.String("c"),
            ],
            "'a' || 'b' || 'c'",
        ),
        (
            "contains",
            [ast.String("abc"), ast.String("b")],
            "'abc' LIKE '%b%'",
        ),
        (
            "endswith",
            [ast.String("abc"), ast.String("bc")],
            "'abc' LIKE '%bc'",
        ),
        (
            "indexof",
            [ast.String("abc"), ast.String("bc")],
            "INSTR('abc', 'bc') - 1",
        ),
        (
            "length",
            [ast.String("a")],
            "length('a')",
        ),
        (
            "length",
            [ast.Identifier("a")],
            'length("a")',
        ),
        (
            "startswith",
            [ast.String("abc"), ast.String("ab")],
            "'abc' LIKE 'ab%'",
        ),
        (
            "substring",
            [ast.String("abc"), ast.Integer("1")],
            "substr('abc', 1 + 1)",
        ),
        (
            "substring",
            [ast.String("abcdef"), ast.Integer("1"), ast.Integer("2")],
            "substr('abcdef', 1 + 1, 2)",
        ),
        ("tolower", [ast.String("ABC")], "lower('ABC')"),
        ("toupper", [ast.String("abc")], "upper('abc')"),
        ("trim", [ast.String(" abc ")], "trim(' abc ')"),
        (
            "year",
            [ast.DateTime("2018-01-01T10:00:00")],
            "strftime('%y', datetime('2018-01-01T10:00:00'))",
        ),
        (
            "month",
            [ast.DateTime("2018-01-01T10:00:00")],
            "strftime('%m', datetime('2018-01-01T10:00:00'))",
        ),
        (
            "day",
            [ast.DateTime("2018-01-01T10:00:00")],
            "strftime('%d', datetime('2018-01-01T10:00:00'))",
        ),
        (
            "hour",
            [ast.DateTime("2018-01-01T10:00:00")],
            "strftime('%H', datetime('2018-01-01T10:00:00'))",
        ),
        (
            "minute",
            [ast.DateTime("2018-01-01T10:00:00")],
            "strftime('%M', datetime('2018-01-01T10:00:00'))",
        ),
        (
            "date",
            [ast.DateTime("2018-01-01T10:00:00")],
            "date(datetime('2018-01-01T10:00:00'))",
        ),
        ("now", [], "datetime('now')"),
        ("round", [ast.Float("123.12")], "round(123.12)"),
        ("floor", [ast.Float("123.12")], "floor(123.12)"),
        ("ceiling", [ast.Float("123.12")], "ceiling(123.12)"),
    ],
)
def test_ast_to_sql_functions(func_name: str, args: List[ast._Node], sql_expected: str):
    inp_ast = ast.Call(ast.Identifier(func_name), args)
    visitor = sql.AstToSqliteSqlVisitor()
    res = visitor.visit(inp_ast)

    assert res == sql_expected
