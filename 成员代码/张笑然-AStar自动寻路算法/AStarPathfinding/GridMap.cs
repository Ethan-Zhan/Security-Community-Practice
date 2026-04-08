using System;
using System.Collections.Generic;
using System.Xml.Linq;

namespace AStarPathfinding
{
    public class GridMap
    {
        private int width;
        private int height;
        private Node[,] grid;

        public GridMap(int width,int height)
        {
            this.width = width;
            this.height = height;
            grid = new Node[width,height];

            // 初始化地图
            for (int x = 0;x < width;x++)
            {
                for (int y = 0;y < height;y++)
                {
                    grid[x,y] = new Node(x,y,true);
                }
            }
        }

        public Node GetNode(int x,int y)
        {
            if (x < 0 || y < 0 || x >= width || y >= height)
                return null;
            return grid[x,y];
        }

        public void SetObstacle(int x,int y)
        {
            grid[x,y].walkable = false;
        }

        public List<Node> GetNeighbors(Node node)// 找邻居节点
        {
            List<Node> neighbors = new List<Node>();

            int[,] directions = new int[,]
            {
                {0,1},{1,0},{0,-1},{-1,0},// 上下左右
                {1,1},{1,-1},{-1,1},{-1,-1} // 对角
            };

            for (int i = 0;i < directions.GetLength(0);i++)
            {
                int nx = node.x + directions[i,0];
                int ny = node.y + directions[i,1];

                Node neighbor = GetNode(nx,ny);
                if (neighbor != null)
                    neighbors.Add(neighbor);
            }

            return neighbors;
        }

        public void PrintMap(List<Node> path,Node start,Node end)
        {
            for (int y = height - 1;y >= 0;y--)
            {
                for (int x = 0;x < width;x++)
                {
                    Node node = grid[x,y];

                    if (node == start)
                        Console.Write("S ");
                    else if (node == end)
                        Console.Write("E ");
                    else if (!node.walkable)
                        Console.Write("# ");
                    else if (path != null && path.Contains(node))
                        Console.Write("* ");
                    else
                        Console.Write(". ");
                }
                Console.WriteLine();
            }
        }
    }
}