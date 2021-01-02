using System.Collections.Generic;

namespace TheInternecineStrife.ServerSide.Model.War.Battle
{

  ///
  /// Тактико-технические характеристики отряда.
  /// Описывает построение отряда и тактику ведения боя. Задается до битвы.
  ///
  public class Formation
  {  	
    // Построение
    public int Columns { get; set; } // Человек в ряду
    public int Rows { get; set; } // Рядов солдат
    public float Density { get; set; } // Плотность человек/м2

    // Тактические характеристики
    public float RangeAttackDistance { get; set; } // С какого расстояния начнется обстрел
    public float RetreetDistance { get; set; } // Отступать, если враг ближе чем, но слишком далеко для ближнего боя
    public float MaleeAttackDistance { get; set; } // На каком расстоянии доставать ножи и топоры
    public int MaleeResource { get; set; } // Степень износа оружия ближнего боя
    public int RangeResource { get; set; } // Запас снарядов для оружия

    // Тактики
    public bool NoBlendMalee { get; set; } // Держать строй или смешаться
    public bool Ranger { get; set; } // Отряд вступает в ближний бой только если его догонят
    public bool FireOnMarsh { get; set; } // Отряд стреляет на ходу. В противном случае он стреляет с позиций.

    // Лазарет
    public List<int> Woundeds { get; set; }
    public int Medics { get; set; }
  }
}
