import numpy as np
from numpy.testing import assert_equal
import pytest
import scipy.sparse as sp

import finch


def test_scipy_coo(arr2d):
    sp_arr = sp.coo_matrix(arr2d, dtype=np.int64)
    finch_arr = finch.Tensor(sp_arr)
    lvl = finch_arr._obj.body.lvl

    assert np.shares_memory(sp_arr.row, lvl.tbl[1].data)
    assert np.shares_memory(sp_arr.col, lvl.tbl[0].data)
    assert np.shares_memory(sp_arr.data, lvl.lvl.val)

    assert_equal(finch_arr.todense(), sp_arr.todense())
    new_arr = finch.permute_dims(finch_arr, (1, 0))
    assert_equal(new_arr.todense(), sp_arr.todense().transpose())


@pytest.mark.parametrize("cls", [sp.csc_matrix, sp.csr_matrix])
def test_scipy_compressed2d(arr2d, cls):
    sp_arr = cls(arr2d, dtype=np.int64)
    finch_arr = finch.Tensor(sp_arr)
    lvl = finch_arr._obj.body.lvl.lvl

    assert np.shares_memory(sp_arr.indices, lvl.idx.data)
    assert np.shares_memory(sp_arr.indptr, lvl.ptr.data)
    assert np.shares_memory(sp_arr.data, lvl.lvl.val)

    assert_equal(finch_arr.todense(), sp_arr.todense())
    new_arr = finch.permute_dims(finch_arr, (1, 0))
    assert_equal(new_arr.todense(), sp_arr.todense().transpose())


@pytest.mark.parametrize(
    "format_with_cls_with_order", [
        ("coo", sp.coo_matrix, "C"),
        ("coo", sp.coo_matrix, "F"),
        ("csc", sp.csc_matrix, "F"),
        ("csr", sp.csr_matrix, "C"),
    ]
)
def test_to_scipy_sparse(format_with_cls_with_order):
    format, sp_class, order = format_with_cls_with_order
    np_arr = np.random.default_rng(0).random((4, 5))
    np_arr = np.array(np_arr, order=order)

    finch_arr = finch.asarray(np_arr, format=format)

    actual = finch_arr.to_scipy_sparse()

    assert isinstance(actual, sp_class)
    assert_equal(actual.todense(), np_arr)


def test_to_scipy_sparse_invalid_input():
    finch_arr = finch.asarray(np.ones((3,3,3)), format="dense")

    with pytest.raises(ValueError, match="Can only convert a 2-dimensional array"):
        finch_arr.to_scipy_sparse()

    finch_arr = finch.asarray(np.ones((3,4)), format="dense")

    with pytest.raises(ValueError, match="Invalid format. Tensor should be a COO, CSR or CSC."):
        finch_arr.to_scipy_sparse()
