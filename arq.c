void A()
{
    Escolha uma producao - A, A->x1, x2, ..., xk for (i = 1 ateh k)
    {
        if (xi eh um nao terminal)
        {
            ativa procedimento xi();
        }
        else if (xi igual ao simbolo de entrada a)
        {
            avance a entrada ao proximo simbolo
        }
        else
        {
            ocorreu um erro
        }
    }
}